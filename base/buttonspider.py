# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import logging
import time

import scrapy
from scrapy_selenium import SeleniumRequest
from proxy.data5u import PROXY_THREAD
from proxy.pool import POOL
from scrapy.http import Response
from selenium.webdriver.chrome.webdriver import WebDriver


class ButtonSpider(scrapy.Spider):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    exclusive = False

    def __init__(self, with_proxy: bool = True):
        super(scrapy.Spider, self).__init__()
        self.with_proxy = with_proxy
        if self.with_proxy:
            self.proxyThread = PROXY_THREAD
            self.proxyThread.start()
            # each proxy need 5 seconds to start, there will be 16 proxies required to start
            time.sleep(5)

    def parse(self, response: Response):
        pass

    @staticmethod
    def get_driver(response: Response) -> WebDriver:
        """
        Obtains the web driver from response

        :param response: response object
        :return: WebDriver
        """
        return response.meta.get('driver', None)

    def handle_failure_selenium(self, failure):
        self.log('fail to collect {}\n{}'.format(failure.request.url, failure), level=logging.ERROR)
        if self.with_proxy:
            POOL.remove(failure.request.meta['proxy'])
        # try with a new proxy
        self.log('restart from the failed url {}'.format(failure.request.url), level=logging.INFO)
        yield SeleniumRequest(
            url=failure.request.url,
            callback=failure.request.callback,
            # try a new proxy
            errback=self.handle_failure_selenium)

    def handle_failure(self, failure):
        self.log('fail to collect {}\n{}'.format(failure.request.url, failure), level=logging.ERROR)
        if self.with_proxy:
            POOL.remove(failure.request.meta['proxy'])
        # try with a new proxy
        self.log('restart from the failed url {}'.format(failure.request.url), level=logging.INFO)
        yield scrapy.Request(
            url=failure.request.url,
            callback=failure.request.callback,
            # try a new proxy
            meta={'proxy': POOL.get() if not self.exclusive else POOL.pop()},
            errback=self.handle_failure)
