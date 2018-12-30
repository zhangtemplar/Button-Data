# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import time

import scrapy

from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class PedataExitSpider(ButtonSpider):
    name = 'pedata_exit'
    allowed_domains = ['exit.pedata.cn']
    start_urls = ['https://exit.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_exit')
    industry = [
        '758', '759', '766', '777', '782', '791', '793', '805', '824', '825', '830', '837', '845', '849', '850', '872',
        '876', '893', '906', '919', '941', '966', '975', '7572', '7573', '7574', '7575', '7577', '7578']
    stage = [
        '1061', '1064', '1065', '1067', '1066', '1062', '1068', '7641', '7854', '1063', '4122', '7699', '7700', '2491']
    header = {
        u'退出企业': 0, u'退出机构': 1, u'资本类型': 2, u'回报金额': 3, u'回报倍数': 4, u'退出方式': 5, u'退出时间': 6,
        u'详情': 7}
    year = range(2018, 2006, -1)

    def __init__(self):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    @staticmethod
    def format_url(industry, year, page=1):
        return 'https://exit.pedata.cn/list_{}_0_{}_0_{}.html'.format(page, industry, year)

    @staticmethod
    def decode_url(url: str) -> (str, str, int):
        """
        Decodes industry, stage and page from the url.

        :param url:
        :return: (industry, stage, page)
        """
        segments = url.split('/')[-1].split('.')[0].split('_')
        return segments[3], segments[5], int(segments[1]),

    def start_requests(self):
        for url in self.start_urls:
            for industry in self.industry:
                for year in self.year:
                    yield scrapy.Request(
                        url=url,
                        dont_filter=True,
                        callback=self.apply_filter,
                        meta={'proxy': POOL.get(), 'extra': {'industry': industry, 'year': year}},
                        errback=self.handle_failure)

    def apply_filter(self, response):
        url = self.format_url(
            response.request.meta['extra']['industry'],
            response.request.meta['extra']['year'])
        self.log('Process page {}'.format(url), level=logging.INFO)
        yield response.follow(
            url=url,
            dont_filter=True,
            callback=self.parse,
            meta={'proxy': response.request.meta['proxy']},
            errback=self.handle_failure)

    def parse(self, response):
        file_name = os.path.join(self.work_directory, response.request.url.split('/')[-1])
        if not os.path.exists(file_name):
            result = []
            for row in response.xpath("//tr[contains(@class, 'table_bg')]"):
                columns = row.xpath("td")
                company = {
                    'name': columns[self.header[u'退出企业']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'退出企业']].xpath('a/@title').extract_first()}
                investor = {
                    'name': columns[self.header[u'退出机构']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'退出机构']].xpath('a/@title').extract_first()}
                keyword = columns[self.header[u'资本类型']].xpath('text()').extract_first()
                invest_time = columns[self.header[u'退出时间']].xpath('text()').extract_first()
                amount = columns[self.header[u'回报金额']].xpath('text()').extract_first()
                gain = columns[self.header[u'回报倍数']].xpath('text()').extract_first()
                exit_type = columns[self.header[u'退出方式']].xpath('text()').extract_first()
                detail = columns[self.header[u'详情']].xpath('a/@href').extract_first()
                result.append({
                    'time': invest_time,
                    'company': company,
                    'investor': investor,
                    'keyword': keyword,
                    'gain': gain,
                    'amount': amount,
                    'type': exit_type,
                    'detail': detail})
            if len(result) < 1:
                self.log('Page {} contains not result'.format(response.request.url), level=logging.WARNING)
                return
            with open(file_name, 'wb') as fo:
                fo.write(response.body)
            with open(file_name.split('.')[0] + '.json', 'w') as fo:
                json.dump(result, fo, ensure_ascii=False)
        # go to next page
        next_page = response.xpath("//a[@title='下一页']/@href").extract_first()
        if next_page is not None:
            self.log('Next page {}'.format(next_page), level=logging.INFO)
            time.sleep(random.random())
            yield response.follow(
                url=next_page,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy']},
                errback=self.handle_failure)
        else:
            # try to build the page by ourself
            industry, year, page = self.decode_url(response.request.url)
            page += 1
            url = self.format_url(industry, year, page)
            self.log('Next page (manually) {}'.format(url), level=logging.INFO)
            yield response.follow(
                url=url,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy']},
                errback=self.handle_failure)
