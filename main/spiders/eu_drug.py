# -*- coding: utf-8 -*-
from scrapy_selenium import SeleniumRequest
from scrapy.http.response import Response
from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class EuDrugSpider(ButtonSpider):
    """
    This class processes the drug approved by Europe Medical Administrative.
    https://www.ema.europa.eu/en/medicines
    """
    name = 'Europe Union'
    allowed_domains = ['https://www.ema.europa.eu/en/medicines/']
    start_urls = []
    rows_to_skip = 9

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.apply_filter,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure_selenium)

    def login(self, response: Response):
        """
        Logs in.

        :param response:
        """
        pass

    def apply_filter(self, response: Response):
        """
        Selects the filter for list of investors

        :param response:
        """
        pass

    def parse_investor_list(self, response: Response):
        """
        Parses the investor list

        :param response:
        """
        pass

    def parse_investor_page(self, response: Response):
        """
        Parses the investor page

        :param response:
        """
        pass

    def parse(self, response: Response):
        pass
