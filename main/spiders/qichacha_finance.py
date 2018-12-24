# -*- coding: utf-8 -*-
import logging
import os

from urllib.parse import parse_qs, urlparse
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.webdriver import WebDriver

from base.buttonspider import ButtonSpider
from proxy.pool import POOL
import copy


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

    def __init__(self):
        super().__init__(self)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    @staticmethod
    def format_url(province, industry, stage, page=1):
        if page == 1:
            return 'https://www.qichacha.com/elib_financing?province={province}&city=&county=&round={stage}&date=&industry={industry}&date='.format(
                province=province, industry=industry, stage=stage)
        else:
            return 'https://www.qichacha.com/elib_financing?province={province}&city=&county=&round={stage}&date=&industry={industry}&date=&p={page}'.format(
                province=province, industry=industry, stage=stage, page=page)

    def start_requests(self):
        for url in self.start_urls:
            for p in self.province:
                for i in self.industry:
                    for r in self.round:
                        yield SeleniumRequest(
                            url=url,
                            callback=self.parse,
                            meta={
                                'proxy': POOL.get(),
                                'extra': {'province': p, 'industry': i, 'round': r}},
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                            },
                            errback=self.handle_failure)

    @staticmethod
    def parse_url(url):
        return parse_qs(urlparse(url).query)

    @staticmethod
    def get_driver(response):
        # type: (object) -> WebDriver
        """
        Obtains the web driver from response

        :param response: response object
        :return: WebDriver
        """
        return response.meta['driver']

    def next_page(self, response):
        arguments = copy.copy(response.request.meta['extra'])
        driver = self.get_driver(response)
        next_page = driver.find_elements_by_xpath("//nav/ul/li/a[@class='next']")
        if len(next_page) < 1:
            return
        arguments['page'] += 1
        next_page = self.format_url(arguments['province'], arguments['industry'], arguments['round'], arguments['page'])
        self.log('go to page {}'.format(next_page), level=logging.INFO)
        yield SeleniumRequest(
            url=next_page,
            callback=self.parse,
            # reuse the current proxy
            meta={'proxy': response.request.meta['proxy'], 'extra': arguments},
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            },
            errback=self.handle_failure)

    def parse(self, response):
        arguments = copy.copy(response.request.meta['extra'])
        if os.path.exists(os.path.join(
                self.work_directory,
                '{}_{}_{}_{}'.format(
                    arguments['province'], arguments['round'], arguments['industry'], arguments.get('p')))):
            # next page
            self.log('page {} already processed'.format(response.request.url))
            self.next_page(response)
        elif 'page' not in arguments:
            # select the filter
            arguments['page'] = 1
            url = self.format_url(arguments['province'], arguments['industry'], arguments['round'], arguments['page'])
            self.log('go to page {}'.format(url), level=logging.INFO)
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                # reuse the current proxy
                meta={'proxy': response.request.meta['proxy'], 'extra': arguments},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                },
                errback=self.handle_failure)
        else:
            # process the real data
            self.log('Process page {}'.format(response.request.url), level=logging.INFO)
            driver = self.get_driver(response)
            row = driver.find_elements_by_xpath("//table[@class='ntable']/tbody/tr")
            first_row = True
            for r in row:
                if first_row:
                    first_row = False
                    continue
                image = r.find_element_by_xpath('td[1]/img').get_attribute('src')
                project_name = r.find_element_by_xpath('td[2]/a').text
                project_url = r.find_element_by_xpath('td[2]/a').get_attribute('src')
                investor = r.find_element_by_xpath('td[3]').text
                stage = r.find_element_by_xpath('td[4]').text
                time = r.find_element_by_xpath('td[5]').text
                yield {'image': image, 'project': {'url': project_url, 'name': project_name}, 'investor': investor,
                       'stage': stage, 'time': time}
                self.log('find investment from {} to {}'.format(investor, project_name), level=logging.INFO)
            # save the file
            open(
                os.path.join(
                    self.work_directory,
                    '{}_{}_{}_{}'.format(
                        arguments['province'], arguments['round'], arguments['industry'], arguments.get('p'))),
                'w').close()
