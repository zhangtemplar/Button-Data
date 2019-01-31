# -*- coding: utf-8 -*-
import json
import logging
import os
import uuid

from scrapy import Request
from scrapy.http.response import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.webdriver import WebDriver

from base.buttonspider import ButtonSpider
from base.template import create_product, create_company


class CfdaSpider(ButtonSpider):
    name = 'cfda'
    allowed_domains = ['app2.sfda.gov.cn']
    start_urls = [
        'http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?formRender=cx&optionType=V1',
        'http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?formRender=cx&optionType=V2',
        'http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?formRender=cx&optionType=V3',
        'http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?formRender=cx&optionType=V4',
    ]
    # without login, you could get at most 40 datas
    data_per_page = 40
    work_directory = os.path.expanduser('~/Downloads/cfda')

    def __init__(self):
        super().__init__(False)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_category,
                errback=self.handle_failure)

    @staticmethod
    def get_driver(response: Response) -> WebDriver:
        """
        Obtains the web driver from response

        :param response: response object
        :return: WebDriver
        """
        return response.meta['driver']

    def parse_category(self, response):
        """
        Parses the category

        :param response:
        """
        file_name = os.path.join(self.work_directory, uuid.uuid5(uuid.NAMESPACE_URL, response.url).hex)
        with open(file_name + '.html', 'wb') as fo:
            fo.write(response.body)
        driver = self.get_driver(response)
        for i in range(15):
            for postfix in ('', '-', '-'):
                rows = driver.find_elements_by_id('{}{}'.format(i, postfix))
                if len(rows) < 1:
                    continue
                # click
                rows[0].click()
                # find the more
                links = driver.find_elements_by_id('abc')
                if len(links) < 1:
                    continue
                category_link = links[0].get_attribute('href')
                self.log('category: {}'.format(category_link), level=logging.INFO)
                # check that page
                yield SeleniumRequest(
                    url=category_link,
                    dont_filter=True,
                    callback=self.parse_list,
                    errback=self.handle_failure)
        # go to the next page
        def _get_next_page_link(driver: WebDriver) -> str or None:
            pagers = driver.find_elements_by_xpath('//body/center/table[3]/tbody/tr[2]/td/center/table/tbody/tr[3]/td/table[2]/tbody/tr/td[2]/table/tbody/tr/td[4]/a')
            if len(pagers) > 0:
                return pagers[0].get_attribute('href')
            return None
        next_page = _get_next_page_link(driver)
        if next_page == response.url:
            return
        self.log('page: {}'.format(next_page))
        yield SeleniumRequest(
            url=next_page,
            dont_filter=True,
            callback=self.parse_category,
            errback=self.handle_failure)

    def parse_list(self, response):
        """
        Parses the investor list

        :param response:
        """
        file_name = os.path.join(self.work_directory, uuid.uuid5(uuid.NAMESPACE_URL, response.url).hex)
        with open(file_name + '.html', 'wb') as fo:
            fo.write(response.body)
        driver = self.get_driver(response)
        for row in driver.find_elements_by_xpath('/html/body/center/table[2]/tbody/tr/td/table/tbody/tr/td/table[1]/tbody/tr/td[2]/a'):
            page_link = row.get_attribute('href')
            self.log('product: {}'.format(page_link))
            yield Request(
                url=page_link,
                dont_filter=True,
                callback=self.parse_product,
                errback=self.handle_failure)
        # go to the next page
        def _get_next_page_link(driver: WebDriver) -> str or None:
            pagers = driver.find_elements_by_xpath('//body/center/table[2]/tbody/tr/td/table/tbody/tr/td/table[2]/tbody/tr/td[2]/table/tbody/tr/td[3]/a[1]')
            if len(pagers) > 0:
                return pagers[0].get_attribute('href')
            return None
        next_page = _get_next_page_link(driver)
        if next_page != response.url:
            # check that page
            yield SeleniumRequest(
                url=next_page,
                dont_filter=True,
                callback=self.parse_list,
                errback=self.handle_failure)

    def parse_product(self, response):
        """
        Parses the investor page

        :param response:
        """
        file_name = os.path.join(self.work_directory, uuid.uuid5(uuid.NAMESPACE_URL, response.url).hex)
        if os.path.exists(file_name):
            self.log('already processed: {}'.format(response.url))
            return
        with open(file_name + '.html', 'wb') as fo:
            fo.write(response.body)

        product_table = self._table_to_dict(
            response,
            '/html/body/center/table[2]/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr')
        product = create_product()
        product['name'] = product_table.get('产品名称', '')
        product['ref'] = product_table.get('批准文号', response.url)
        product['abs'] = product_table.get('英文名称', '')
        product['tag'] = [product_table.get('剂型', ''), product_table.get('产品类别', '')]
        product['asset']['lic'] = [
            product_table.get('批准文号', ''), product_table.get('药品本位码', ''), product_table.get('原批准文号', '')]
        product['addr']['line1'] = product_table.get('生产地址', '')
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = 'China'
        product['asset']['market'] = '# 批准日期\n{}\n# 药品本位码备注\n{}\n'.format(
            product_table.get('批准日期', ''), product_table.get('药品本位码备注', ''))

        company_table = self._table_to_dict('/html/body/center/table[2]/tbody/tr/td/table[5]/tbody/tr/td/table[1]/tbody/tr[1]')
        company = create_company()
        company['ref'] = company_table.get('编号', company_table.get('社会信用代码/组织机构代码', response.url))
        company['addr']['line1'] = company_table.get('注册地址', '')
        company['addr']['city'] = 'Unknown'
        company['addr']['state'] = company_table.get('省份', '')
        company['addr']['country'] = 'China'
        company['entr']['market'] = company_table.get('生产范围', '')
        company['entr']['tech'] = company_table.get('生产地址', '')
        company['name'] = company_table.get('企业名称	', '')
        company['abs'] = company['name']
        company['intro'] = self._dict_to_markdown_table({k: company_table[k] for k in (
            '有效期至', '发证日期', '发证机关', '签发人', '日常监管机构', '日常监管人员', '社会信用代码/组织机构代码',
            '监督举报电话', '备注', '分类码	', '法定代表人', '企业负责人', '质量负责人'
        )})
        with open(file_name + '.json', 'wb') as fo:
            json.dump({'product': product, 'company': company}, fo)

        # check other product
        for link in response.xpath('/html/body/center/table[2]/tbody/tr/td/table[5]/tbody/tr/td/table[8]/tbody/tr/td/table/tbody/tr/td[1]/a'):
            yield response.follow(
                url=link.xpath('@href').extra_first(),
                dont_filter=True,
                callback=self.parse_product,
                errback=self.handle_failure)

    @staticmethod
    def _table_to_dict(response: Response, xpath: str) -> dict:
        result = {}
        for row in response.xpath(xpath):
            keys = [column.xpath('text()').extra_first() for column in row.xpath('th')]
            values = [column.xpath('text()').extra_first() for column in row.xpath('td')]
            for k, v in zip(keys, values):
                if len(k) < 1:
                    continue
                result[k] = v
        return result

    @staticmethod
    def _dict_to_markdown_table(table: dict) -> dict:
        result = '|   |   |\n| --- | --- |\n'
        for k in sorted(table.keys()):
            result += '| {} | {} |\n'.format(k, table[k])
        return result
