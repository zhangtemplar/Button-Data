# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from urllib.parse import urlparse, parse_qs

from scrapy.http.response import Response
from scrapy_selenium import SeleniumRequest
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from base.buttonspider import ButtonSpider
from base.template import create_product, create_company


class CfdaSpider(ButtonSpider):
    name = 'cfda'
    allowed_domains = ['app1.sfda.gov.cn']
    start_urls = [
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=25&tableName=TABLE25&title=%B9%FA%B2%FA%D2%A9%C6%B7&bcId=152904713761213296322795806604',
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=36&tableName=TABLE36&title=%BD%F8%BF%DA%D2%A9%C6%B7&bcId=152904858822343032639340277073',
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=26&tableName=TABLE26&title=%B9%FA%B2%FA%C6%F7%D0%B5&bcId=152904417281669781044048234789',
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=27&tableName=TABLE27&title=%BD%F8%BF%DA%C6%F7%D0%B5&bcId=152904442584853439006654836900',
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=68&tableName=TABLE68&title=%B9%FA%B2%FA%CC%D8%CA%E2%D3%C3%CD%BE%BB%AF%D7%B1%C6%B7&bcId=152904508268669766289794835880',
        'http://app1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=69&tableName=TABLE69&title=%BD%F8%BF%DA%BB%AF%D7%B1%C6%B7&bcId=152904517090916554369932355535',
    ]
    base_url = 'http://app1.sfda.gov.cn/datasearchcnda/face3/'
    # without login, you could get at most 40 datas
    data_per_page = 40
    work_directory = os.path.expanduser('~/Downloads/cfda')

    def __init__(self):
        super().__init__(True, True)
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def handle_failure(self, failure):
        self.log('fail to collect {}\n{}'.format(failure.request.url, failure), level=logging.ERROR)
        # try with a new proxy
        self.log('restart from the failed url {}'.format(failure.request.url), level=logging.INFO)
        yield SeleniumRequest(
            url=failure.request.url,
            callback=failure.request.callback,
            # try a new proxy
            errback=failure.request.errback)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_list,
                errback=self.handle_failure)

    @staticmethod
    def _last_page(driver: WebDriver):
        elements = driver.find_elements_by_xpath('//*[@id="content"]/div/table[4]/tbody/tr/td[1]')
        if len(elements) < 1:
            return True
        match = re.finditer(r'第 ([0-9]+) 页 共([0-9]+)页 共166845条', elements[0].text)
        current = None
        total = None
        for m in match:
            if current is None:
                current = m.group()
            elif total is None:
                total = m.group()
        if current is None or total is None:
            return True
        return current == total

    @staticmethod
    def _extract_url(text):
        match = re.finditer(r'"(.+)"', text)
        for m in match:
            return CfdaSpider.base_url + m.group(1)
        return None

    @staticmethod
    def _next_page(driver: WebDriver):
        try:
            pagers = driver.find_elements_by_xpath('//*[@id="content"]/div/table[4]/tbody/tr/td[5]/img')
            if len(pagers) < 1:
                return False
            pagers[0].click()
            return True
        except WebDriverException as e:
            pass
        except StaleElementReferenceException as e:
            pass

    def parse_list(self, response):
        """
        Parses the investor list

        :param response:
        """
        driver = self.get_driver(response)
        page = 1
        while True:
            links = []
            for t in range(3):
                try:
                    for row in driver.find_elements_by_xpath('//*[@id="content"]/div/table[2]/tbody/tr/td/p/a'):
                        page_link = self._extract_url(row.get_attribute('href'))
                        if page_link is None:
                            self.log(
                                'fail to extract link from {}'.format(row.text),
                                level=logging.ERROR)
                            continue
                        self.log('product: {}'.format(page_link), level=logging.INFO)
                        links.append(page_link)
                    break
                except StaleElementReferenceException as e:
                    self.log('retry again due to {}'.format(e), level=logging.ERROR)
            if not self._next_page(driver):
                break
            page += 1
            self.log('process page {}'.format(page), level=logging.INFO)
            if self._last_page(driver):
                self.log('last page found', level=logging.INFO)
                break
        driver.quit()
        for link in links:
            yield SeleniumRequest(
                url=link,
                dont_filter=True,
                callback=self.parse_product,
                wait_time=10,
                wait_until=EC.presence_of_element_located((By.XPATH, '//body/div/div/table[1]/tbody')),
                errback=self.handle_failure)

    def parse_domestic_drug(self, table: dict):
        product = create_product()
        product['name'] = self.use_nonempty(table['产品名称'], table['英文名称'])
        product['abs'] = table['商品名']
        product['intro'] = table['英文名称']
        product['asset']['lic'] = [table['批准文号'], table['药品本位码'], table['原批准文号']]
        product['addr']['line1'] = table['生产地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = '中国'
        product['tag'] = [table['剂型'], table['产品类别'], 'Drug']
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in ('规格', '批准日期', '药品本位码备注')})

        return {'product': product}

    @staticmethod
    def use_nonempty(*argv):
        for a in argv:
            if len(a) > 0:
                return a
        return ''

    def parse_import_drug(self, table: dict):
        product = create_product()
        product['name'] = self.use_nonempty(table['商品名（中文）'], table['商品名（英文）'])
        product['abs'] = self.use_nonempty(table['产品名称（中文）'], table['产品名称（英文）'])
        product['intro'] = table['商品名（英文）']
        product['asset']['lic'] = [table['注册证号'], table['原注册证号'], table['分包装批准文号'], table['药品本位码']]
        product['addr']['line1'] = table['生产地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = '中国'
        product['tag'] = [table['剂型（中文）'], table['产品类别'], 'Drug']
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in (
                '产品名称（英文）', '包装规格（中文）', '规格（中文）', '发证日期', '有效期截止日', '药品本位码备注')})

        company = create_company()
        company['name'] = self.use_nonempty(table['公司名称（英文）'], table['公司名称（中文）'])
        company['addr']['city'] = 'Unknown'
        company['addr']['line1'] = self.use_nonempty(table['地址（英文）'], table['地址（中文）'])
        company['addr']['country'] = self.use_nonempty(table['国家/地区（英文）'], table['国家/地区（中文）'])

        manufacture = create_company()
        manufacture['name'] = self.use_nonempty(table['生产厂商（英文）'], table['生产厂商（中文）'])
        manufacture['addr']['city'] = 'Unknown'
        manufacture['addr']['line1'] = self.use_nonempty(table['厂商地址（英文）'], table['厂商地址（中文）'])
        manufacture['addr']['country'] = self.use_nonempty(table['厂商国家/地区（英文）'], table['厂商国家/地区（中文）'])

        return {'product': product, 'company': company, 'manufacture': manufacture}

    def parse_domestic_device(self, table: dict):
        product = create_product()
        product['name'] = table['产品名称	']
        product['abs'] = table['适用范围	']
        product['intro'] = table['结构及组成']
        product['asset']['lic'] = [table['注册证编号'], table['产品标准']]
        product['addr']['line1'] = table['生产地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = '中国'
        product['addr']['zip'] = table['邮编']
        product['tag'] = [table['剂型（中文）'], table['产品类别'], 'Medical Device']
        product['asset']['market'] = self._dict_to_markdown_table(
            {k: table[k] for k in (
                '型号、规格', '其他内容', '备注', '批准日期', '有效期至', '变更日期', '变更情况', '审批部门')})
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in (
                '主要组成成分（体外诊断试剂）', '预期用途（体外诊断试剂）', '产品储存条件及有效期（体外诊断试剂）')})

        company = create_company()
        company['name'] = table['注册人名称']
        company['addr']['city'] = 'Unknown'
        company['addr']['line1'] = table['注册人住所']
        company['addr']['country'] = 'China'

        delegate = create_company()
        delegate['name'] = table['代理人名称']
        delegate['addr']['city'] = 'Unknown'
        delegate['addr']['line1'] = table['代理人住所']
        delegate['addr']['country'] = 'China'

        return {'product': product, 'company': company, 'delegate': delegate}

    def parse_import_device(self, table: dict):
        product = create_product()
        product['name'] = self.use_nonempty(table['产品名称'], table['产品名称（中文）'])
        product['abs'] = table['适用范围	']
        product['intro'] = table['结构及组成']
        product['asset']['lic'] = [table['注册证编号'], table['产品标准']]
        product['addr']['line1'] = table['生产地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = self.use_nonempty(table['生产国或地区（英文）'], '中国')
        product['addr']['zip'] = table['邮编']
        product['tag'] = [table['剂型（中文）'], table['产品类别'], 'Medical Device']
        product['asset']['market'] = self._dict_to_markdown_table(
            {k: table[k] for k in (
                '产品名称（中文）', '型号、规格', '其他内容', '备注', '批准日期', '有效期至', '变更日期', '变更情况', '审批部门',
                '售后服务机构')})
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in (
                '主要组成成分（体外诊断试剂）', '预期用途（体外诊断试剂）', '产品储存条件及有效期（体外诊断试剂）')})

        company = create_company()
        company['name'] = table['注册人名称']
        company['addr']['city'] = 'Unknown'
        company['addr']['line1'] = table['注册人住所']
        company['addr']['country'] = 'China'

        delegate = create_company()
        delegate['name'] = table['代理人名称']
        delegate['addr']['city'] = 'Unknown'
        delegate['addr']['line1'] = table['代理人住所']
        delegate['addr']['country'] = 'China'

        manufacture = create_company()
        manufacture['name'] = table['生产厂商名称（中文）']
        manufacture['addr']['city'] = 'Unknown'
        manufacture['addr']['country'] = table['生产国或地区（中文）']

        return {'product': product, 'company': company, 'delegate': delegate, 'manufacture': manufacture}

    def parse_domestic_cosmetic(self, table: dict):
        product = create_product()
        product['name'] = table['产品名称']
        product['abs'] = table['产品名称备注']
        product['asset']['lic'] = [table['批准文号'], table['卫生许可证号']]
        product['addr']['line1'] = table['生产企业地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = '中国'
        product['tag'] = [table['产品类别'], 'Cosmetic']
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in ('批件状态', '批准日期', '批件有效期', '备注')})

        manufacture = create_company()
        manufacture['name'] = table['生产企业	']
        manufacture['addr']['city'] = 'Unknown'
        manufacture['addr']['line1'] = table['生产企业地址']
        manufacture['addr']['country'] = 'China'

        return {'product': product, 'manufacture': manufacture}

    def parse_import_cosmetic(self, table: dict):
        product = create_product()
        product['name'] = self.use_nonempty(table['产品名称（中文）'], table['产品名称（英文）'])
        product['abs'] = self.use_nonempty(table['产品名称（英文）'], table['产品名称（中文）'])
        product['intro'] = table['产品名称备注']
        product['asset']['lic'] = [table['批准文号']]
        product['addr']['line1'] = table['生产企业地址']
        product['addr']['city'] = 'Unknown'
        product['addr']['country'] = table['生产国（地区）']
        product['tag'] = [table['产品类别'], 'Cosmetic']
        product['asset']['tech'] = self._dict_to_markdown_table(
            {k: table[k] for k in ('批件状态', '批准日期', '批件有效期', '备注')})

        company = create_company()
        company['name'] = self.use_nonempty(table['生产企业（中文）'], table['生产企业（英文）'])
        company['addr']['city'] = 'Unknown'
        company['addr']['line1'] = table['生产企业地址']
        company['addr']['country'] = table['生产国（地区）']

        delegate = create_company()
        delegate['name'] = table['在华申报责任单位']
        delegate['addr']['city'] = 'Unknown'
        delegate['addr']['line1'] = table['在华申报责任单位']
        delegate['addr']['country'] = 'China'

        return {'product': product, 'company': company, 'delegate': delegate}

    def parse_product(self, response):
        """
        Parses the investor page

        :param response:
        """
        parameter = parse_qs(urlparse(response.url).query)
        category = parameter['tableView'][0]
        product_id = parameter['Id'][0]
        file_name = os.path.join(self.work_directory, category + product_id)
        if os.path.exists(file_name):
            self.log('already processed: {}'.format(response.url))
            return
        with open(file_name + '.html', 'wb') as fo:
            fo.write(response.body)
        return
        driver = self.get_driver(response)
        table = self._table_to_dict(driver, '//body/div/div/table[1]/tbody/tr')
        if category == '国产药品':
            data = self.parse_domestic_drug(table)
        elif category == '进口药品':
            data = self.parse_import_drug(table)
        elif category == '国产器械':
            data = self.parse_domestic_device(table)
        elif category == '进口器械':
            data = self.parse_import_device(table)
        else:
            self.log('unknown type', level=logging.ERROR)
            return
        data['product']['ref'] = response.url
        with open(file_name + '.json', 'w') as fo:
            json.dump(data, fo)

    @staticmethod
    def _table_to_dict(response: WebDriver, xpath: str) -> dict:
        result = {}
        for row in response.find_elements_by_xpath(xpath):
            columns = row.find_elements_by_xpath('td')
            if len(columns) < 2:
                continue
            key = columns[0].text
            value = columns[1].text
            result[key] = value
        return result

    @staticmethod
    def _dict_to_markdown_table(table: dict) -> dict:
        result = '|   |   |\n| --- | --- |\n'
        for k in sorted(table.keys()):
            result += '| {} | {} |\n'.format(k, table[k])
        return result
