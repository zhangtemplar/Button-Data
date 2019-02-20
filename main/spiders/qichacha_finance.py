# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import time
from urllib.parse import parse_qs, urlparse

import scrapy

from base.buttonspider import ButtonSpider
from proxy.pool import POOL


class QichachaFinanceButtonSpider(ButtonSpider):
    """
    Extracts Qichacha finance information.

    Note native Request will not work, we will need selenium.
    """
    name = 'qichacha'
    allowed_domains = ['qichacha.com']
    start_urls = [
        'https://www.qichacha.com/elib_financing']
    work_directory = os.path.expanduser('~/Downloads/qichacha')
    round = range(1, 9)
    industry = range(0, 44)
    province = [
        'BJ', 'TJ', 'HB', 'SX', 'NMG', 'LN', 'JL', 'HLJ', 'SH', 'JS', 'ZJ', 'AH', 'FJ', 'JX', 'SD', 'HN', 'HUB', 'HUN',
        'GD', 'GX', 'HAIN', 'CQ', 'SC', 'GZ', 'YN', 'XZ', 'SAX', 'GS', 'QH', 'NX', 'XJ', 'TW', 'HK', 'MO']
    header = {
        u'产品图片': 0,
        u'产品名称': 1,
        u'所属公司': 2,
        u'投资机构': 3,
        u'融资阶段': 4,
        u'融资金额': 5,
        u'融资时间': 6,
    }

    def __init__(self=True):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    @staticmethod
    def format_url(province, industry, stage, page=1):
        if page == 1:
            return 'https://www.qichacha.com/elib_financing?province={province}&city=&county=&round={stage}&date=&industry={industry}'.format(
                province=province, industry=industry, stage=stage)
        else:
            return 'https://www.qichacha.com/elib_financing?province={province}&city=&county=&round={stage}&date=&industry={industry}&p={page}'.format(
                province=province, industry=industry, stage=stage, page=page)

    def start_requests(self):
        for url in self.start_urls:
            for p in self.province:
                for i in self.industry:
                    for r in self.round:
                        self.log('start page province={} industry={} and round={}'.format(p, i, r), level=logging.INFO)
                        yield scrapy.Request(
                            url=url,
                            dont_filter=True,
                            callback=self.apply_filter,
                            meta={
                                'proxy': POOL.get(),
                                'extra': {'province': p, 'industry': i, 'round': r}},
                            errback=self.handle_failure)

    @staticmethod
    def parse_url(url):
        return parse_qs(urlparse(url).query)

    def next_page(self, response):
        next_page = response.xpath("//nav/ul/li/a[@class='next']/@href").extract_first()
        if next_page is None:
            self.log('cannot find next page', level=logging.WARN)
            return
        self.log('next page {}'.format(next_page), level=logging.INFO)
        return response.follow(
            url=next_page,
            callback=self.parse,
            # reuse the current proxy
            meta={'proxy': response.request.meta['proxy']},
            errback=self.handle_failure)
        time.sleep(random.random())

    def navigate(self, response, url):
        self.log('go to page {}'.format(url), level=logging.INFO)
        return response.follow(
            url=url,
            callback=self.parse,
            # reuse the current proxy
            meta={'proxy': response.request.meta['proxy']},
            errback=self.handle_failure)

    def extract_page(self, response):
        arguments = self.parse_url(response.request.url)
        self.log('Process page {}'.format(response.request.url), level=logging.INFO)
        with open(
                os.path.join(
                    self.work_directory,
                    '{}_{}_{}_{}.html'.format(arguments['province'][0], arguments['round'][0],
                                              arguments['industry'][0], arguments.get('p', ['1'])[0])),
                'wb') as fo:
            fo.write(response.body)
        row = response.xpath("//table[@class='ntable']/tr")
        if len(row) < 1:
            self.log('page {} has no data'.format(response.request.url), level=logging.WARNING)
            POOL.remove(response.request.meta['proxy'])
            return
        first_row = True
        result = []
        for r in row:
            if first_row:
                first_row = False
                continue
            image = r.xpath('td[1]/img/@src').extract_first()
            project_name = r.xpath('td[2]/a/text()').extract_first()
            project_url = r.xpath('td[2]/a/@src').extract_first()
            investor = r.xpath('td[3]/text()').extract_first()
            stage = r.xpath('td[4]/text()').extract_first()
            invest_time = r.xpath('td[5]/text()').extract_first()
            result.append({
                'image': image,
                'project': {'url': project_url, 'name': project_name},
                'investor': investor,
                'stage': stage,
                'time': invest_time})
            self.log('find investment from {} to {}'.format(investor, project_name), level=logging.INFO)
        # save the file
        with open(
                os.path.join(
                    self.work_directory,
                    '{}_{}_{}_{}.json'.format(arguments['province'][0], arguments['round'][0],
                                              arguments['industry'][0], arguments.get('p', ['1'])[0])),
                'w') as fo:
            json.dump(result, fo, ensure_ascii=False)

    def apply_filter(self, response):
        arguments = response.request.meta['extra']
        # need to select the filter first
        page = self.skip_processed(arguments)
        url = self.format_url(arguments['province'], arguments['industry'], arguments['round'], page)
        yield self.navigate(response, url)

    def skip_processed(self, arguments):
        page = 1
        while os.path.exists(os.path.join(
                self.work_directory,
                '{}_{}_{}_{}.json'.format(
                    arguments['province'], arguments['round'], arguments['industry'], page))):
            # skip the processed and go to next page
            page += 1
            self.log('skip page {}'.format(page), level=logging.INFO)
        # start from this page
        return page

    def parse(self, response):
        # process the real data
        self.extract_page(response)
        # go to next page
        yield self.next_page(response)
