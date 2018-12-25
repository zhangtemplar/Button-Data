# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import scrapy
from proxy.pool import POOL
from proxy.data5u import GetProxyThread
import time


class ButtonSpider(scrapy.Spider):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

    def __init__(self, with_proxy=True):
        super(scrapy.Spider, self).__init__()
        self.with_proxy = with_proxy
        if self.with_proxy:
            self.proxyThread = GetProxyThread()
            self.proxyThread.start()
            # wait for 10 seconds to build the pool
            time.sleep(10)

    @staticmethod
    def close(spider, reason):
        proxyThread = spider.__getattribute__('proxyThread')
        if proxyThread is not None:
            spider.proxyThread.close()

    def handle_failure(self, failure):
        if self.with_proxy:
            POOL.remove(failure.request.meta['proxy'])