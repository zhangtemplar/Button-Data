# -*- coding: utf-8 -*-
from scrapy_selenium import SeleniumRequest

from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class XiniuDataSpider(ButtonSpider):
    name = 'xiniu_data'
    allowed_domains = ['http://www.xiniudata.com']
    start_urls = ['http://http://www.xiniudata.com/']
    # without login, you could get at most 40 datas
    data_per_page = 40

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.apply_filter,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)

    def login(self, response):
        """
        Logs in.

        :param response:
        """
        pass

    def apply_filter(self, response):
        """
        Selects the filter for list of investors

        :param response:
        """
        pass

    def parse_investor_list(self, response):
        """
        Parses the investor list

        :param response:
        """
        pass

    def parse_investor_page(self, response):
        """
        Parses the investor page

        :param response:
        """
        pass

    def parse(self, response):
        pass
