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


class PedailyIpoSpider(ButtonSpider):
    name = 'pedaliy_ipo'
    allowed_domains = ['zdb.pedaily.cn']
    start_urls = ['https://zdb.pedaily.cn/ipo/']
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

    def find_filter(self, response):
        driver = response.request.meta.get('driver', None)
        if driver is None:
            self.log('Unable to start selenium', level=logging.ERROR)
            return
        more_button = driver.find_elements_by_id('idBoxOpen')
        if len(more_button) < 1:
            self.log('Unable to open category information', level=logging.ERROR)
            return
        more_button[0].click()
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(lambda x: len(x.find_elements_by_xpath("//dd[@id='boxBody']/div")) > 0)
        except:
            self.log('Unable to retrieve category information', level=logging.ERROR)
            return
        result = []
        links = []
        for c in driver.find_elements_by_xpath("//dd[@id='boxBody']/div"):
            category = c.find_element_by_xpath('b/a')
            l1 = {'name': category.text[1:-1], 'url': category.get_attribute('href'), 'children': []}
            result.append(l1)
            self.log('find filter ' + l1['name'], level=logging.DEBUG)
            for s in c.find_elements_by_xpath('p'):
                if len(s.find_elements_by_xpath('b/a')) > 0:
                    sub_category = s.find_element_by_xpath('b/a')
                    l2 = {'name': sub_category.text[1:-1], 'url': sub_category.get_attribute('href'), 'children': []}
                    l1['children'].append(l2)
                    self.log('find filter ' + l2['name'], level=logging.DEBUG)
                else:
                    l2 = l1
                for f in s.find_elements_by_xpath('a'):
                    l2['children'].append({'name': f.text, 'url': f.get_attribute('href'), 'children': []})
                    links.append(f.get_attribute('href'))
        self.log('find filter ' + result.__str__(), level=logging.INFO)
        with open(os.path.join(self.work_directory, 'category.json'), 'w') as fo:
            json.dump(result, fo, ensure_ascii=False)
        return links

    def apply_filter(self, response):
        if os.path.exists(os.path.join(self.work_directory, 'category.json')):
            with open(os.path.join(self.work_directory, 'category.json'), 'r') as fi:
                result = json.load(fi)
            links = []
            for r1 in result:
                for r2 in r1['children']:
                    if len(r2['children']) < 1:
                        links.append(r2['url'])
                    else:
                        links.extend([r3['url'] for r3 in r2['children']])
        else:
            links = self.find_filter(response)
        for l in links:
            url = l.split('/')
            url[-2] = 'ipo/' + url[-2]
            l = '/'.join(url)
            self.log('Process page {}'.format(l), level=logging.INFO)
            yield scrapy.Request(
                url=l,
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
        for row in response.xpath("//ul[@id='ipo-list']/li"):
            if first_row:
                first_row = False
                continue
            invest_time = row.xpath("div/span/text()").extract_first()
            company_name = row.xpath("dl/dt[@class='company']/a/text()").extract_first()
            company_url = row.xpath("dl/dt[@class='company']/a/@href").extract_first()
            industry_name = row.xpath("dl/dt[@class='industry']/a/text()").extract_first()
            industry_url = row.xpath("dl/dt[@class='industry']/a/@href").extract_first()
            amount = row.xpath("dl/dt[@class='money']/span[@class='d']/text()").extract_first()
            unit = row.xpath("dl/dt[@class='money']/span[@class='m']/text()").extract_first()
            if amount is None:
                amount = ''
            elif unit is None:
                pass
            else:
                amount = amount + unit
            place = row.xpath("dl/dt[@class='place']/a/text()").extract_first()
            detail = row.xpath("dl/dt[@class='view']/a/@href").extract_first()
            result.append({
                'time': invest_time,
                'company': {'name': company_name, 'url': company_url},
                'category': industry_name,
                'industry': {'name': industry_name, 'url': industry_url},
                'round': 'ipo',
                'amount': {'amount': amount, 'unit': 'RMB'},
                'place': place,
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
