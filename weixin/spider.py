import requests
from weixin.config import *
from weixin.db import RedisClient
from pyquery import PyQuery as pq


class Spider():
    base_url = 'https://weixin.sogou.com/weixin?query=%s&type=2&page=%s&ie=utf8'
    keyword = '宝多六花'
    params = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    proxies = None
    headers = None
    redis = RedisClient()

    def head(self, snuid):
        """
        获取snuid，拼凑出请求头
        :param snuid: snuid参数
        :return: 请求头
        """
        snuid = snuid[1]
        print('Cookie使用：', snuid)
        cookie = snuid + 'IPLOC=CN3603; SUID=478DA7275218910A000000005BB4C763; weixinIndexVisited=1; SUV=00151DF127A78D475BB4C764498BA456; JSESSIONID=aaaKzrDDD0iwcf7S_fWyw; SMYUV=1539481497473652; UM_distinctid=166703f6f890-0f89813641ce5e-333b5602-100200-166703f6f8a1a7; PHPSESSID=r6s9gp60p8bonj5nbn9ak42fg4; ld=CZllllllll2berZFlllllVsZLI1lllllJicb$kllll9lllll9klll5@@@@@@@@@@; LSTMV=246%2C75; LCLKINT=6255; ABTEST=0|1542511268|v1; ppinf=5|1542694165|1543903765|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo2OlV0b3BpYXxjcnQ6MTA6MTU0MjY5NDE2NXxyZWZuaWNrOjY6VXRvcGlhfHVzZXJpZDo0NDpvOXQybHVIUTk5LUFDd3Z1ZEFzSmJtckNhajk0QHdlaXhpbi5zb2h1LmNvbXw; pprdig=Ev03K1qUPEGid38Q2SatAOOTb4h9G4CDCGNIL5qTlajwdP4iFjwtcIqjKuRGNaLYGGokWecSiHeGAXQwWQm25skRiXqu8vRBACj9ejaxcTpV4lHuU_yIl5bs7OTsaaWyBx1wz9SCMPdqrFUKzSGgQN0PJ63IaDT5EQhyyTUKsVQ; sgid=16-37598605-AVvzpRVIQO87TxrZ9rdxtq4; SUIR=4F34C9486E6B15888DA7BE166F6E5369; SNUID=C226DF5F787C025C95C8952C79C3468F; sct=12; ppmdig=1542812932000000dda27b6ad31fee458e068a05ea2a6467'
        self.params['Cookie'] = cookie
        return self.params

    def test_proxy(self):
        """
        二次清洗代理
        :return:健康代理
        """
        global proxies
        global headers
        url = 'https://weixin.sogou.com/weixin?query=宝多六花&type=2&page=1&ie=utf8'
        proxy = self.redis.proxy_random()
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        try:
            r = requests.get(url, headers=headers, allow_redirects=False, proxies=proxies)
            if r.status_code == 200:
                pass
            else:
                self.redis.proxy_decrease(proxy)
                self.test_proxy()
        except:
            self.redis.proxy_decrease(proxy)
            self.test_proxy()


    def start(self, page):
        global headers
        global proxies
        url = self.base_url %(self.keyword, page)
        try:
            response = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=20)
            print('正在爬取：', url)
            if response and response.status_code in VALID_STATUSE:
                self.parse_index(response)
            if response.status_code == 302:
                headers = self.head(self.redis.snuid_pop())
                response = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=5)
                print('重新爬取：', url)
                self.parse_index(response)
        except:
            self.test_proxy()
            self.start(page)


    def parse_index(self, response):
        """
        解析索引页
        :param response: 响应
        :return: 新的响应
        """
        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            self.redis.request_add(url)
            print('添加url:', url)


    def run(self):
        """
        入口
        :return:
        """
        global headers
        global proxies
        headers = self.head(self.redis.snuid_pop())
        self.test_proxy()
        for i in range(1, 101):
            self.start(i)
        # self.schedule()


if __name__ == '__main__':
    spider = Spider()
    spider.run()
