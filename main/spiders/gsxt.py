# -*- coding: utf-8 -*-
from base.buttonspider import ButtonSpider
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.webdriver import WebDriver
import logging
import time
import os
import uuid
from proxy.pool import POOL


class GsxtButtonSpider(ButtonSpider):
    name = 'gsxt'
    allowed_domains = ['gsxt.gov.cn']
    start_urls = [
        'http://gsxt.gov.cn/',
        'http://www.gsxt.gov.cn/corp-query-entprise-info-hot-search-list.html?province=100000']
    work_directory = os.path.expanduser('~/Downloads/gsxt')


    def __init__(self=True):
        super().__init__(True)


    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url,
                callback=self.parse,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure_selenium)

    def parse(self, response):
        self._parse_report(response)
        self._follow_link(response)

    def _follow_link(self, response):
        driver = self.get_driver(response)
        for element in driver.find_elements_by_xpath('//*[@id="div1"]/table/tbody/tr/td/div/a'):
            self.log('find link {}'.format(element.text), level=logging.INFO)
            yield SeleniumRequest(response.urljoin(element.get_attribute('href')), callback=self.parse)
        for element in driver.find_elements_by_xpath(
                '//div[@class="hot-ent-box"]/div[contains(@class, "hot fl")]/ul/li/a'):
            self.log('find link {}'.format(element.text), level=logging.INFO)
            yield SeleniumRequest(response.urljoin(element.get_attribute('href')), callback=self.parse)

    def _parse_report(self, response):
        driver = self.get_driver(response)
        # verify it is the page for a company
        title = driver.find_elements_by_xpath('//div[@class="fullName"]')
        if len(title) < 1:
            self.log('not a valid page {}'.format(response.url))
            return
        # TODO: need to scroll to the end of page to load more data
        self._parse_base(driver)
        self._parse_charter(driver)
        self._parse_charge(driver)
        self._parse_abnormal(driver)
        self._parse_blacklist(driver)
        # save the file for future use
        filename = uuid.uuid5(uuid.NAMESPACE_URL, response.url.encode('utf-8')).hex
        with open(os.path.join(self.work_directory, filename + '.html'), 'wb') as f:
            f.write(response.body)
        yield {
            'link': response.url,
            'file': filename
        }

    @staticmethod
    def _load_more(driver):
        """
        Loads more data by clicking the `load more` div

        :param driver: current web driver
        :return: None
        """
        element = driver.find_elements_by_xpath("//*[@id='addmore']")
        if len(element) < 1:
            return
        if element[0].get_attribute('style') == 'display: none;':
            # this element has been hidden, which indicate there is no more data to load
            return
        element[0].click()
        # wait for the data to load
        time.sleep(1)

    def _parse_base(self, driver):
        self._parse_base_certificate(driver)
        self._parse_base_shareholder(driver)
        self._parse_base_key_person(driver)
        self._parse_base_branch(driver)
        self._parse_base_ne(driver)
        self._parse_base_clear(driver)
        self._parse_base_alt(driver)
        self._parse_base_mort(driver)
        self._parse_base_copyright(driver)
        self._parse_base_trademark(driver)
        self._parse_base_check(driver)
        self._parse_base_drranins(driver)
        self._parse_base_assist(driver)
        self._parse_base_annual_report(driver)
        self._parse_base_instant_stock(driver)
        self._parse_base_instant_change(driver)
        self._parse_base_instant_licensing(driver)
        self._parse_base_instant_intellectual(driver)
        self._parse_base_instant_copyright(driver)
        self._parse_base_instant_punish(driver)
        self._parse_base_simple_cancel(driver)
        self._parse_base_license_expiration(driver)
        self._parse_base_group_member(driver)

    def _parse_charter(self, driver):
        pass

    def _parse_charge(self, driver):
        pass

    def _parse_abnormal(self, driver):
        pass

    def _parse_blacklist(self, driver):
        pass

    def _parse_base_certificate(self, driver):
        self._load_more(driver)

    def _parse_base_shareholder(self, driver):
        self._load_more(driver)

    def _parse_base_key_person(self, driver):
        self._load_more(driver)

    def _parse_base_branch(self, driver):
        self._load_more(driver)

    def _parse_base_ne(self, driver):
        self._load_more(driver)

    def _parse_base_clear(self, driver):
        self._load_more(driver)

    def _parse_base_alt(self, driver):
        self._load_more(driver)

    def _parse_base_mort(self, driver):
        self._load_more(driver)

    def _parse_base_copyright(self, driver):
        self._load_more(driver)

    def _parse_base_trademark(self, driver):
        self._load_more(driver)

    def _parse_base_check(self, driver):
        self._load_more(driver)

    def _parse_base_drranins(self, driver):
        self._load_more(driver)

    def _parse_base_assist(self, driver):
        self._load_more(driver)

    def _parse_base_annual_report(self, driver):
        self._load_more(driver)

    def _parse_base_instant_stock(self, driver):
        self._load_more(driver)

    def _parse_base_instant_change(self, driver):
        self._load_more(driver)

    def _parse_base_instant_licensing(self, driver):
        self._load_more(driver)

    def _parse_base_instant_intellectual(self, driver):
        self._load_more(driver)

    def _parse_base_instant_copyright(self, driver):
        self._load_more(driver)

    def _parse_base_instant_punish(self, driver):
        self._load_more(driver)

    def _parse_base_simple_cancel(self, driver):
        self._load_more(driver)

    def _parse_base_license_expiration(self, driver):
        self._load_more(driver)

    def _parse_base_group_member(self, driver):
        self._load_more(driver)

