import redis
from weixin.config import *
from random import choice
from weixin.error import PoolEmptyError


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def request_add(self, request):
        """
        向队列添加序列化后的Request
        :param request: 请求对象
        :param fail_time: 失败次数
        :return: 添加结果
        """
        return self.db.rpush(REQUEST_REDIS_KEY, request)

    def request_pop(self):
        """
        取出下一个Request并反序列化
        :return: Request or None
        """
        if self.db.llen(REQUEST_REDIS_KEY):
            return self.db.lpop(REQUEST_REDIS_KEY)
        else:
            return False

    def request_empty(self):
        return self.db.llen(REQUEST_REDIS_KEY) == 0

    def snuid_pop(self):
        """
        移出并获取snuid列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :return: 尾部的snuid
        """
        return self.db.brpop(SNUID_REDIS_KEY)

    def proxy_random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(PROXY_REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(PROXY_REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
               raise PoolEmptyError

    def proxy_decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(PROXY_REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(PROXY_REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(PROXY_REDIS_KEY, proxy)

    def weixin_proxy_random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(WEIXIN_PROXY_REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(WEIXIN_PROXY_REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
               raise PoolEmptyError

    def weixin_proxy_decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(WEIXIN_PROXY_REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(WEIXIN_PROXY_REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(WEIXIN_PROXY_REDIS_KEY, proxy)

if __name__ == '__main__':
    db = RedisClient()


