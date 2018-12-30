# -*- coding: utf-8 -*-
import json
import logging
import os

import scrapy

from main.spiders.pedata import PedataSpider
from proxy.pool import POOL


class PedataInvestSpider(PedataSpider):
    name = 'pedata_invest'
    allowed_domains = ['invest.pedata.cn']
    start_urls = ['https://invest.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_invest')
    header = {
        u'机构名称': 0, u'企业名称': 1, u'所属行业': 2, u'企业标签': 3, u'投资轮次': 4, u'投资金额': 5, u'投资时间': 6,
        u'详情': 7}

    @staticmethod
    def format_url(arguments):
        return 'https://invest.pedata.cn/list_{}_0_{}_{}_{}.html'.format(
            arguments.get('page', 1), arguments['industry'], arguments['stage'], arguments['year'])

    @staticmethod
    def decode_url(url: str):
        arguments = url.split('/')[-1].split('.')[0].split('_')
        return {'page': int(arguments[1]), 'industry': arguments[3], 'stage': arguments[4], 'year': arguments[5]}

    def start_requests(self):
        for url in self.start_urls:
            for industry in self.industry:
                for stage in self.stage:
                    for year in self.year:
                        yield scrapy.Request(
                            url=url,
                            dont_filter=True,
                            callback=self.apply_filter,
                            meta={
                                'proxy': POOL.get() if not self.exclusive else POOL.pop(),
                                'extra': {'industry': industry, 'stage': stage, 'year': year}},
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
                investor = []
                for i in columns[self.header[u'机构名称']].xpath("a"):
                    investor.append(
                        {'name': i.xpath('@title').extract_first(), 'url': i.xpath('@href').extract_first()})
                company = {
                    'name': columns[self.header[u'企业名称']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'企业名称']].xpath('a/@title').extract_first()}
                industry = columns[self.header[u'所属行业']].xpath('text()').extract_first()
                keyword = columns[self.header[u'企业标签']].xpath('text()').extract_first()
                stage = columns[self.header[u'投资轮次']].xpath('text()').extract_first()
                amount = columns[self.header[u'投资金额']].xpath('text()').extract_first()
                invest_time = columns[self.header[u'投资时间']].xpath('text()').extract_first()
                detail = columns[self.header[u'详情']].xpath('a/@href').extract_first()
                result.append({
                    'time': invest_time,
                    'company': company,
                    'industry': industry,
                    'round': stage,
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
