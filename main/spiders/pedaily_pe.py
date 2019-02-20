# -*- coding: utf-8 -*-
import scrapy
import os
import logging
import json
import time
import random
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from proxy.pool import POOL
from base.buttonspider import ButtonSpider


class PedailyPeSpider(ButtonSpider):
    name = 'pedaliy_pe'
    allowed_domains = ['zdb.pedaily.cn']
    start_urls = ['https://zdb.pedaily.cn/pe/']
    work_directory = os.path.expanduser('~/Downloads/pedaily')

    def __init__(self=True):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.apply_filter,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure_selenium)

    def apply_filter(self, response):
        for year in range(2018, 2003, -1):
            url = response.request.url + 'y{}/'.format(year)
            self.log('Process page {}'.format(url), level=logging.INFO)
            yield scrapy.Request(
                url=url,
                dont_filter=True,
                callback=self.parse,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)

    def parse(self, response):
        file_name = os.path.join(self.work_directory, response.request.url.split('/')[-2])
        if os.path.exists(file_name + '.html'):
            self.log('Page {} already processed'.format(response.request.url), level=logging.INFO)
            return
        first_row = True
        result = []
        for row in response.xpath("//ul[@id='pe-list']/li"):
            if first_row:
                first_row = False
                continue
            invest_time = row.xpath("div/span/text()").extract_first()
            company_name = row.xpath("dl/dt[@class='group']/a/text()").extract_first()
            company_url = row.xpath("dl/dt[@class='group']/a/@href").extract_first()
            amount = row.xpath("dl/dt[@class='money']/span[@class='m']/text()").extract_first()
            unit = row.xpath("dl/dt[@class='money']/span[@class='d']/text()").extract_first()
            fund_name = row.xpath("dl/dt[@class='fund']/a/text()").extract_first()
            fund_url = row.xpath("dl/dt[@class='fund']/a/@href").extract_first()
            detail = row.xpath("dl/dt[@class='view']/a/@href").extract_first()
            result.append({
                'time': invest_time,
                'company': {'name': company_name, 'url': company_url},
                'round': 'unknown',
                'amount': {'amount': amount, 'unit': unit},
                'fund': {'name': fund_name, 'url': fund_url},
                'detail': detail})
        with open(file_name + '.html', 'wb') as fo:
            fo.write(response.body)
        with open(file_name + '.json', 'w') as fo:
            json.dump(result, fo, ensure_ascii=False)
        # go to next page
        next_page = response.xpath(
            "//div[@class='page-list page']/a[@class='next' and text()='下一页']/@href").extract_first()
        if next_page is not None:
            time.sleep(random.random())
            yield response.follow(
                url=next_page,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy']},
                errback=self.handle_failure)
