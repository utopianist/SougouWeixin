import requests
from weixin.config import *
from weixin.db import RedisClient
from weixin.mysql import MySQL
from pyquery import PyQuery as pq

class Articles():
    headers = {
        'Host': 'mp.weixin.qq.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://mp.weixin.qq.com/s?src=11&timestamp=1543224952&ver=1268&signature=n0EW*NEa73Cd39RmRKfaYPU5NUDuN5X6eypDap*--nQ913dIIe3i8EcRnyd7PptsjOAKzDVuI*ikSsioBg0*zMGPbB27CUrORDvEMav2hvZHp2tFF3V4cNyl09Cr73Rl&new=1',
        'Cookie': 'rewardsn=; wxtokenkey=777',
        'Connection': 'keep-alive',
    }
    redis = RedisClient()
    mysql = MySQL()
    proxies = None

    def test_proxy(self):
        """

        :return:
        """
        global proxies
        url = 'https://mp.weixin.qq.com'
        proxy = self.redis.weixin_proxy_random()
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        try:
            r = requests.get(url, headers=self.headers, allow_redirects=False, proxies=proxies, timeout=30)
            if r.status_code == 200:
                pass
            else:
                self.redis.weixin_proxy_decrease(proxy)
                self.test_proxy()
        except:
            self.redis.weixin_proxy_decrease(proxy)
            self.test_proxy()


    def start(self):
        """
        调用self.header方法，构造请求头headers
        向redis的requests队列传送第一个request
        """
        global proxies
        while not self.redis.request_empty():
            url = self.redis.request_pop()
            try:
                response = requests.get(url, headers=self.headers, proxies=proxies, allow_redirects=True, timeout=20)
                print('正在爬取：', url)
                print(response.status_code)
                if response and response.status_code in VALID_STATUSE:
                    print('status_code:200')
                    self.parse_detail(response)
                else:
                    self.test_proxy()
                    self.redis.request_add(url)
            except:
                self.test_proxy()
                self.redis.request_add(url)


    def parse_detail(self, response):
        """
        解析详情页
        :param response: 响应
        :return: 微信公众号文章
        """
        doc = pq(response.text)
        data = {
            'title': doc('.rich_media_title').text(),
            'content': doc('.rich_media_content').text(),
            'date': doc('#post-date').text(),
            'nickname': doc('#js_profile_qrcode > div > strong').text(),
            'wechat': doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        }
        if not len(data) == 0:
            self.mysql.insert('articles', data)

if __name__ == '__main__':
    articles = Articles()
    articles.test_proxy()
    articles.start()