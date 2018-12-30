# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import time

import scrapy

from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class PedataMaSpider(ButtonSpider):
    name = 'pedata_ma'
    allowed_domains = ['ma.pedata.cn']
    start_urls = ['https://ma.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_ma')
    industry = [
        '758', '759', '766', '777', '782', '791', '793', '805', '824', '825', '830', '837', '845', '849', '850', '872',
        '876', '893', '906', '919', '941', '966', '975', '7572', '7573', '7574', '7575', '7577', '7578']
    stage = ['1118', '1117', '1116']
    status = ['7718', '7713', '7715', '7723']
    header = {
        u'并购方': 0, u'被并购方': 1, u'所属行业': 2, u'并购类型': 3, u'并购状态': 4, u'并购金额': 5, u'并购时间': 6,
        u'详情': 7}
    year = range(2018, 2006, -1)

    def __init__(self):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    @staticmethod
    def format_url(industry, year, page=1):
        return 'https://ma.pedata.cn/list_{}_0_0_{}_{}.html'.format(page, industry, year)

    @staticmethod
    def decode_url(url: str) -> (str, str, int):
        """
        Decodes industry, stage and page from the url.

        :param url:
        :return: (industry, stage, page)
        """
        segments = url.split('/')[-1].split('.')[0].split('_')
        return segments[4], segments[5], int(segments[1]),

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
                investor = {
                    'name': columns[self.header[u'并购方']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'并购方']].xpath('a/@title').extract_first()}
                company = {
                    'name': columns[self.header[u'被并购方']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'被并购方']].xpath('a/@title').extract_first()}
                industry = columns[self.header[u'所属行业']].xpath('text()').extract_first()
                keyword = columns[self.header[u'并购类型']].xpath('text()').extract_first()
                status = columns[self.header[u'并购状态']].xpath('text()').extract_first()
                amount = columns[self.header[u'并购金额']].xpath('text()').extract_first()
                invest_time = columns[self.header[u'并购时间']].xpath('text()').extract_first()
                detail = columns[self.header[u'详情']].xpath('a/@href').extract_first()
                result.append({
                    'time': invest_time,
                    'company': company,
                    'industry': industry,
                    'status': status,
                    'amount': amount,
                    'keyword': keyword,
                    'investor': investor,
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
            # try to build the page by ourselves
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
