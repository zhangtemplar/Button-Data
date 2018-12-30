# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import time

import scrapy

from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class PedataSpider(ButtonSpider):
    """
    Base class for pedata.
    """
    name = 'pedata'
    work_directory = None
    industry = {
        '758', '759', '766', '777', '782', '791', '793', '805', '824', '825', '830', '837', '845', '849', '850', '872',
        '876', '893', '906', '919', '941', '966', '975', '7572', '7573', '7574', '7575', '7577', '7578'}
    stage = {
        '1061', '1064', '1065', '1067', '1066', '1062', '1068', '7641', '7854', '1063', '4122', '7699', '7700', '2491'}
    year = {str(y) for y in range(2018, 2006, -1)}
    exclusive = True

    def __init__(self):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    @staticmethod
    def format_url(arguments: dict) -> str:
        """
        Formats an url for crawl from arguments.

        You must implement this method in subclass

        :param arguments: a dictionary
        :return the formatted url
        """
        raise NotImplementedError()

    @staticmethod
    def decode_url(url: str) -> (str, str, int):
        """
        Decodes industry, stage and page from the url.

        :param url:
        :return: {str:str}
        """
        arguments = url.split('/')[-1].split('.')[0].split('_')
        return {'page': int(arguments[1]), 'industry': arguments[3], 'stage': arguments[4], 'year': arguments[5]}

    @staticmethod
    def valid_url(url: str) -> bool:
        """
        Validates an url.

        :param url: url
        :return: True if the url is a valid url for crawl
        """
        arguments = PedataSpider.decode_url(url)
        return arguments['year'] in PedataSpider.year

    def apply_filter(self, response: scrapy.http.Response) -> scrapy.Request:
        """
        Applies the filter to the request.

        :param response: response object
        """
        url = self.format_url(response.request.meta['extra'])
        self.log('Process page {}'.format(url), level=logging.INFO)
        yield response.follow(
            url=url,
            dont_filter=True,
            callback=self.parse,
            meta={'proxy': response.request.meta['proxy']},
            errback=self.handle_failure)

    def next_page(self, response: scrapy.http.Response) -> scrapy.Request:
        """
        Goes to next page.

        :param response: response object
        :return: request for next page
        """
        # go to next page
        next_url = response.xpath("//a[@title='下一页']/@href").extract_first()
        if next_url is not None:
            self.log('Next page {}'.format(next_url), level=logging.INFO)
            time.sleep(random.random())
            return response.follow(
                url=next_url,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy']},
                errback=self.handle_failure)
        else:
            # try to build the page by ourself
            arguments = self.decode_url(response.request.url)
            arguments['page'] += 1
            url = self.format_url(arguments)
            self.log('Next page (manually) {}'.format(url), level=logging.INFO)
            return response.follow(
                url=url,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy']},
                errback=self.handle_failure)
