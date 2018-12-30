# -*- coding: utf-8 -*-
import json
import logging
import os

import scrapy

from main.spiders.pedata import PedataSpider
from proxy.pool import POOL


class PedataExitSpider(PedataSpider):
    name = 'pedata_exit'
    allowed_domains = ['exit.pedata.cn']
    start_urls = ['https://exit.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_exit')
    header = {
        u'退出企业': 0, u'退出机构': 1, u'资本类型': 2, u'回报金额': 3, u'回报倍数': 4, u'退出方式': 5, u'退出时间': 6,
        u'详情': 7}

    @staticmethod
    def format_url(arguments):
        return 'https://exit.pedata.cn/list_{}_0_{}_0_{}.html'.format(
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
        yield self.next_page(response)
