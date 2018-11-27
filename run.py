from weixin.spider import Spider
from weixin.articles import Articles

def main():
    spider = Spider()
    spider.run()
    articles = Articles()
    articles.test_proxy()
    articles.start()


if __name__ == '__main__':
    main()