# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from copy import deepcopy

from scrapy_selenium import SeleniumRequest
from scrapy.http import Response
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, remove_head_tail_white_space, remove_empty_string_from_array, extract_phone, extract_dictionary
from proxy.pool import POOL
from dateutil.parser import parse


class JohnsHopkinsSpider(ButtonSpider):
    name = 'JohnsHopkins University'
    allowed_domains = ['otd.harvard.edu']
    start_urls = ['http://jhu.technologypublisher.com/']
    address = {
        'line1': '1812 Ashland Avenue',
        'line2': 'Suite 110',
        'city': 'Baltimore',
        'state': 'MD',
        'zip': '21205',
        'country': 'USA'}
    item_per_page = 20
    page = 0

    def __init__(self):
        super().__init__(False)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_list,
                wait_time=30,
                wait_until=expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='hits-container']/div")),
                errback=self.handle_failure_selenium)

    def parse_name_from_url(self, url):
        elements = url.split("title=")
        if len(elements) > 1:
            return elements[-1]
        return url.split("/")[-1]

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for link in response.xpath("//div[@class='hit-content']/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        total_result = self.statictics(response)
        self.page += 1
        if self.page * self.item_per_page < total_result:
            self.log('process page {}'.format(self.page), level=logging.INFO)
            yield SeleniumRequest(
                url='http://jhu.technologypublisher.com/?q=&hPP=20&idx=Prod_Inteum_TechnologyPublisher_jhu&p={}'.format(self.page),
                dont_filter=True,
                wait_time=30,
                callback=self.parse_list,
                wait_until=expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='hit-content']/a")),
                errback=self.handle_failure_selenium)
        for p in patent_links:
            name = self.parse_name_from_url(p)
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield SeleniumRequest(
                url=p,
                callback=self.parse,
                dont_filter=True,
                wait_time=30,
                errback=self.handle_failure_selenium)

    def statictics(self, response: Response) -> int:
        """
        Get the meta data of the patent from the table.

        :return total result
        """
        text = response.xpath('//div[@class="ais-body ais-stats--body"]/div/text()').get()
        if text is None:
            return 0
        for m in re.finditer(r'([0-9,]+)', text):
            try:
                return int(m.group().replace(',', ''))
            except:
                pass
        return 0

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = self.parse_name_from_url(response.url)
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['name'] = response.xpath("string(//h1)").get()
        for text in response.xpath("//div[@id='divDisclosureDate']/text()").getall():
            try:
                product['created'] = parse(text).strftime("%a, %d %b %Y %H:%M:%S GMT")
                break
            except:
                pass
        meta = self.get_meta(response)
        market = extract_dictionary(meta, 'Need|need|Market|market|Value')
        product['asset']['market'] = '\n'.join(market.values())
        tech = extract_dictionary(meta, 'Technology|Technical')
        product['asset']['tech'] = '\n'.join(tech.values())
        content = remove_head_tail_white_space(response.xpath("string(//td[1]/div[@class='c_tp_description'])").get())
        product['abs'] = content[:content.find('. ') + 1]
        if len(product['abs']) < 1:
            product['abs'] = content
        for k in market:
            del meta[k]
        for k in tech:
            del meta[k]
        product['intro'] = dictionary_to_markdown(meta)
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        product['tag'] = self.add_tags(response)
        contact = self.get_contact(response)
        product['contact'] = contact

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors, 'contact': contact}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        text = remove_head_tail_white_space(response.xpath("string(//td[1]/div[@class='c_tp_description'])").get())
        titles = response.xpath("//td[1]/div[@class='c_tp_description']/b/text()").getall()
        if len(titles) < 1:
            return {'Abstract': text}
        start = text.find(titles[0])
        result = {}
        for t in range(1, len(titles)):
            end = text.find(titles[t])
            result[titles[t - 1]] = text[start + len(titles[t - 1]): end]
            start = end
        result[titles[-1]] = text[start + len(titles[-1]):]
        return result

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for name in response.xpath("//div[@id='inventorLinks']/div/a/text()"):
            if len(name) < 1:
                continue
            user = create_user()
            user['name'] = name
            user['exp']['exp']['company'] = self.name
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors

    def add_tags(self, response: Response) -> list:
        """
        Add keywords to the project.

        :param response: Response object
        :return a list of inventors
        """
        return remove_empty_string_from_array(response.xpath("//div[@id='categoryLinks']/div/a/text()").getall())

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: the contact information
        """,
        contact = {"website": "", "meet": "", "email": "", "phone": ""}
        email = response.xpath("//div[@class='c_tp_contact']/a/text()").get()
        if email is not None:
            contact['email'] = email
        phone = extract_phone(response.xpath("string(//div[@class='c_tp_contact'])").get())
        if len(phone) > 0:
            contact['phone'] = phone[0]
        return contact
