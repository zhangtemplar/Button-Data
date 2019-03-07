# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from copy import deepcopy

from scrapy import Request
from scrapy.http import Response

from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, remove_head_tail_white_space, remove_empty_string_from_array, \
    extract_phone, extract_dictionary
from proxy.pool import POOL


class VanderbiltSpider(ButtonSpider):
    """
    Extract the common logic for *.technologypublisher.com, which is provided by Inteum LLC.
    """
    name = 'Vanderbilt University'
    allowed_domains = ['cttc.co']
    start_urls = ['https://cttc.co/technologies']
    next_page_template = 'https://cttc.co/technologies?page=0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C{}'
    address = None
    item_per_page = 10
    page = 0
    title_xpath = "string(//h1[@class='page-header'])"
    abstract_filter = 'Description|description|Summary'
    market_filter = 'Need|need|Market|market|Value|Application|Advantage'
    tech_filter = 'Technology|Technical'

    def __init__(self, with_proxy: bool = False):
        super().__init__(with_proxy)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)

    def parse_name_from_url(self, url):
        elements = url.split("title=")
        if len(elements) > 1:
            return elements[-1]
        return url.split("/")[-1]

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for link in response.xpath("//div[@class='view-content']/div[contains(@class, 'views-row')]//h2/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        total_result = self.statictics(response)
        self.page += 1
        if self.page * self.item_per_page < total_result:
            self.log('process page {}'.format(self.page), level=logging.INFO)
            yield response.follow(
                url=self.next_page_template.format(self.page),
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)
        for p in patent_links:
            name = self.parse_name_from_url(p)
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield response.follow(
                url=p,
                callback=self.parse,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)

    def statictics(self, response: Response) -> int:
        """
        Get the meta data of the patent from the table.

        :return total result
        """
        text = response.xpath('//*[@id="block-system-main"]/div/div[2]/h3/text()').get()
        if text is None:
            return 0
        for m in re.finditer(r'([0-9]+)$', text):
            try:
                return int(m.group())
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
        product['name'] = response.xpath(self.title_xpath).get()
        meta = self.get_meta(response)
        abstract = extract_dictionary(meta, self.abstract_filter)
        product['abs'] = '\n'.join(abstract.values())
        market = extract_dictionary(meta, self.market_filter)
        product['asset']['market'] = '\n'.join(market.values())
        tech = extract_dictionary(meta, self.tech_filter)
        product['asset']['tech'] = '\n'.join(tech.values())
        for k in market:
            if k in meta:
                del meta[k]
        for k in tech:
            if k in meta:
                del meta[k]
        for k in abstract:
            if k in meta:
                del meta[k]
        product['intro'] = dictionary_to_markdown(meta)
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        product['tag'] = self.add_tags(response)
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        contact = self.get_contact(response)
        contact['abs'] = 'Inventor of ' + product['name']
        contact['addr'] = product['addr']
        contact['tag'] = product['tag']
        product['contact'] = contact['contact']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors, 'contact': contact}, fo)

    def get_meta(self, response):
        result = {}
        title = 'Description'
        for row in response.xpath("//div[@class='field-items']/div/*"):
            text = remove_head_tail_white_space(row.xpath("string()").get())
            if len(text) < 1:
                continue
            if len(row.xpath(
                    "span[@style=\"font-family: 'Times New Roman';font-style: Normal;font-weight: bold;font-size: 16px;text-decoration: underline;\"]")) > 0:
                title = text
            else:
                result[title] = result.get(title, '') + '\n' + text
        return result

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for name in response.xpath("//div[@class='inventors']/a/text()").getall():
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
        return remove_empty_string_from_array(
            response.xpath("//span[contains(@class, 'label')]/a/text()").getall())

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: the contact information
        """
        user = create_user()
        user['name'] = response.xpath("//div[@class='case-manager']/a/text()").get()
        user['ref'] = response.urljoin(response.xpath("//div[@class='case-manager']/a/@href").get())
        user['contact']['website'] = user['ref']
        user['contact']['email'] = response.xpath("//div[@class='case-manager']/span/a/text()").get()
        if user['contact']['email'] is None:
            user['contact']['email'] = ''
        phone = extract_phone(response.xpath("string(//div[@class='case-manager'])").get())
        if len(phone) > 0:
            user['contact']['phone'] = phone[0]
        return user
