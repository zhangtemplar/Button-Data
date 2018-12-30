# -*- coding: utf-8 -*-
import json
import logging
import os

import scrapy

from main.spiders.pedata import PedataSpider
from proxy.pool import POOL


class PedataIpoSpider(PedataSpider):
    name = 'pedata_ipo'
    allowed_domains = ['ipo.pedata.cn']
    start_urls = ['https://ipo.pedata.cn/list_1_0_0_0_0.html']
    work_directory = os.path.expanduser('~/Downloads/pedata_ipo')
    header = {
        u'上市企业': 0, u'股票代码': 1, u'上市时间': 2, u'交易所': 3, u'行业': 4, u'地区': 5, u'主办券商': 6,
        u'VC/PE支持': 7, u'详情': 8}

    def format_url(self, arguments):
        return 'https://ipo.pedata.cn/list_{}_0_0_{}_{}.html'.format(
            arguments.get('page', 1), arguments['industry'], arguments['year'])

    def decode_url(self, url: str):
        arguments = url.split('/')[-1].split('.')[0].split('_')
        return {'page': int(arguments[1]), 'industry': arguments[4], 'year': arguments[5]}

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
                    'name': columns[self.header[u'上市企业']].xpath('a/@href').extract_first(),
                    'url': columns[self.header[u'上市企业']].xpath('a/@title').extract_first()}
                code = columns[self.header[u'股票代码']].xpath('text()').extract_first()
                invest_time = columns[self.header[u'上市时间']].xpath('text()').extract_first()
                exchange = columns[self.header[u'交易所']].xpath('text()').extract_first()
                industry = columns[self.header[u'行业']].xpath('text()').extract_first()
                address = columns[self.header[u'地区']].xpath('text()').extract_first()
                broker = columns[self.header[u'主办券商']].xpath('text()').extract_first()
                vc_pe = columns[self.header[u'VC/PE支持']].xpath('text()').extract_first()
                detail = columns[self.header[u'详情']].xpath('a/@href').extract_first()
                result.append({
                    'time': invest_time,
                    'company': company,
                    'industry': industry,
                    'code': code,
                    'exchange': exchange,
                    'broker': broker,
                    'address': address,
                    'vc_pe': vc_pe,
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
