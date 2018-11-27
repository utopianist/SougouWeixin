# Redis数据库地址
REDIS_HOST = 'localhost'

# Redis端口
REDIS_PORT = 6379

# Redis密码，如无填None
REDIS_PASSWORD = None

SNUID_REDIS_KEY = 'SougouWeixin'
PROXY_REDIS_KEY = 'proxies'
REQUEST_REDIS_KEY = 'requests'
WEIXIN_PROXY_REDIS_KEY = 'weixinproxies'

# snuid池数量界限
POOL_UPPER_THRESHOLD = 50000

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5000

#最大评分
MAX_SCORE = 100
MIN_SCORE = 0

#爬取间隔
SLEEPTIME = 10
#最大失败数
MAX_FAILED_TIME = 2

# 开关
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True
#爬取超时时间
TIMEOUT = 20
#合法状态码
VALID_STATUSE = [200]

MYSQL_HOST = 'localhost'

MYSQL_PORT = 3306

MYSQL_USER = 'root'

MYSQL_PASSWORD = '123456'

MYSQL_DATABASE = 'weixin'
