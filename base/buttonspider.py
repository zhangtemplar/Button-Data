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

from proxy.data5u import PROXY_THREAD
from proxy.pool import POOL


class ButtonSpider(scrapy.Spider):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

    def __init__(self, with_proxy=True):
        super(scrapy.Spider, self).__init__()
        self.with_proxy = with_proxy
        if self.with_proxy:
            self.proxyThread = PROXY_THREAD
            self.proxyThread.start()
            # wait for 10 seconds to build the pool
            time.sleep(10)

    def handle_failure(self, failure):
        self.log('fail to collect {}\n{}'.format(failure.request.url, failure), level=logging.ERROR)
        if self.with_proxy:
            POOL.remove(failure.request.meta['proxy'])
        # try with a new proxy
        self.log('restart from the failed url {}'.format(failure.request.url), level=logging.INFO)
        yield scrapy.Request(
            url=failure.request.url,
            callback=self.parse,
            # try a new proxy
            meta={'proxy': POOL.get()},
            errback=self.handle_failure)
