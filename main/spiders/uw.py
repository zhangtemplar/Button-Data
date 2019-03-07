# -*- coding: utf-8 -*-
import json
import logging
import os
import time
from copy import deepcopy

from scrapy import Request
from scrapy.http import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

from base.buttonspider import ButtonSpider
from base.template import create_user, create_product
from base.util import remove_empty_string_from_array, remove_head_tail_white_space, extract_phone


class WashingtonSpider(ButtonSpider):
    name = 'University of Washington'
    allowed_domains = ['jhu.technologypublisher.com']
    start_urls = ['https://els.comotion.uw.edu/uw-search-technology']
    address = {
        'line1': '022 Odegaard',
        'line2': '',
        'city': 'Seattle',
        'state': 'WA',
        'zip': '98195',
        'country': 'USA'}
    title_xpath = "string(//h1)"
    market_filter = 'Need|need|Market|market|Value|Application|Advantage|novelty'

    def __init__(self, with_proxy: bool = False):
        super().__init__(with_proxy)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_list,
                errback=self.handle_failure_selenium)

    def parse_name_from_url(self, url):
        elements = url.split("title=")
        if len(elements) > 1:
            return elements[-1]
        return url.split("/")[-1]

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        driver = self.get_driver(response)
        button = driver.find_element_by_xpath("//input[@value='Select All']")
        button.click()
        time.sleep(3)
        button = driver.find_element_by_xpath("//input[@value='Search']")
        button.click()
        WebDriverWait(driver, 10).until(presence_of_element_located(
            (By.XPATH, "//div[@id='bdp-results']/div[@class='bdp']/a")),
            "fail to load results")
        patent_links = []
        for row in driver.find_elements_by_xpath("//div[@id='bdp-results']/div[@class='bdp']/a"):
            text = row.text
            url = row.get_attribute('href')
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        for p in patent_links:
            name = self.parse_name_from_url(p)
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield Request(
                url=p,
                callback=self.parse,
                dont_filter=True,
                errback=self.handle_failure)

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = self.parse_name_from_url(response.url)
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['name'] = response.xpath("//h2/a/text()").get()
        content = response.xpath("//div[@class='bdp']/p/text()").getall()
        if len(content) > 0:
            product['abs'] = content[0][:content[0].find('. ') + 1]
        product['intro'] = '\n'.join(content)
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        product['tag'] = self.add_tags(response)
        contact = self.get_contact(response)
        contact['abs'] = 'Contact of ' + product['name']
        contact['addr'] = self.add_tags(response)
        product['contact'] = contact['contact']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'contact': contact}, fo)

    def get_contact(self, response: Response) -> dict:
        """
        Get contact information of the project.

        :param response: Response object
        :return a list of inventors
        """
        user = create_user()
        email = response.xpath("//div[@class='tech-manager']/a/@href").get()[len('mailto:'):]
        name = response.xpath("//div[@class='tech-manager']/a/text()").get()
        user['name'] = name
        user['contact']['email'] = email if email is not None else ''
        phone = extract_phone(response.xpath("//div[@class='tech-manager']/text()").get())
        if len(phone) > 0:
            user['contact']['phone'] = phone
        return user

    def add_tags(self, response: Response) -> list:
        """
        Add keywords to the project.

        :param response: Response object
        :return a list of inventors
        """
        return remove_empty_string_from_array(
            [remove_head_tail_white_space(t) for t in response.xpath(
                "//div[@class='bdp']/p[contains(text(), 'Categories')]/text()").get().split(':')[-1].split('|')])
