# -*- coding: utf-8 -*-
import json
import logging
import os

import scrapy

from main.spiders.pedata import PedataSpider
from proxy.pool import POOL


class PedataMaSpider(PedataSpider):
    name = 'pedata_ma'
    allowed_domains = ['ma.pedata.cn']
    start_urls = ['https://ma.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_ma')
    header = {
        u'并购方': 0, u'被并购方': 1, u'所属行业': 2, u'并购类型': 3, u'并购状态': 4, u'并购金额': 5, u'并购时间': 6,
        u'详情': 7}

    @staticmethod
    def format_url(arguments):
        return 'https://ma.pedata.cn/list_{}_0_{}_0_{}.html'.format(
            arguments.get('page', 1), arguments['industry'], arguments['year'])

    def start_requests(self):
        for url in self.start_urls:
            for industry in self.industry:
                for year in self.year:
                    yield scrapy.Request(
                        url=url,
                        dont_filter=True,
                        callback=self.apply_filter,
                        meta={
                            'proxy': POOL.get() if not self.exclusive else POOL.pop(),
                            'extra': {'industry': industry, 'year': year}},
                        errback=self.handle_failure)

    def parse(self, response):
        if not self.valid_url(response.request.url):
            self.log('Page {} is not valid'.format(response.request.url))
            return

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

        yield self.next_page(response)
