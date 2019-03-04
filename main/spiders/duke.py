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
from base.util import dictionary_to_markdown, extract_phone, remove_head_tail_white_space, \
    remove_empty_string_from_array
from proxy.pool import POOL


class DukeSpider(ButtonSpider):
    name = 'Duke University'
    allowed_domains = ['olv.duke.edu']
    start_urls = ['https://olv.duke.edu/technologies/']
    address = {
        'line1': '2812 ERWIN ROAD',
        'line2': 'Sts 306',
        'city': 'DURHAM',
        'state': 'NC',
        'zip': '27705',
        'country': 'USA'}

    def __init__(self):
        super().__init__(False)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                callback=self.parse_list,
                errback=self.handle_failure)

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for link in response.xpath("//a[@class='lead-in']/@href").getall():
            patent_links.append(link)
        # for next page
        next_page = response.xpath("//div[@class='nav-previous']/a/@href").get()
        if next_page is not None:
            self.log('process page {}'.format(next_page), level=logging.INFO)
            yield response.follow(
                url=next_page,
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)
        for p in patent_links:
            name = p.split('/')[-2]
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield response.follow(
                url=p,
                callback=self.parse,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = response.url.split('/')[-2]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['name'] = response.xpath("string(//h1)").get()
        meta = self.get_meta(response)
        abstract = self._extract_dictionary(meta, 'Advantage|advantage|Abstract')
        product['abs'] = '\n'.join(abstract.values())
        if len(product['abs']) < 1:
            product['abs'] = next(iter(meta.values()))
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        product['asset']['tech'] = dictionary_to_markdown(meta, ('Technology',))
        product['asset']['market'] = dictionary_to_markdown(meta, ('Value Proposition', 'Value proposition'))
        for k in abstract:
            del meta[k]
        for key in ('Value Proposition', 'Value proposition', 'Technology'):
            if key in meta:
                del meta[key]
        product['intro'] = dictionary_to_markdown(meta)
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        product['tag'] = self.add_tags(response)
        product['contact'] = self.get_contact(response)

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        result = {}
        title = 'Abstract'
        # Note: if running with JS, the data can be found in //div[@id='dynamic_content']/table[2]/tbody/tr
        for row in response.xpath("//div[@class='technology-content user-content']/*"):
            if row.xpath("strong/text()").get() is not None:
                title = row.xpath("strong/text()").get()
            if row.xpath("b/text()").get() is not None:
                title = row.xpath("b/text()").get()
            elif row.xpath("name()").get() == 'h3':
                title = row.xpath("string()").get()
            elif title is not None:
                result[title] = result.get(title, '') + '\n' + row.xpath("string()").get()
        return result

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for name in response.xpath("//li[@class='inventor']/text()").getall():
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
        return remove_empty_string_from_array(
            [remove_head_tail_white_space(t) for t in
             response.xpath("//ul[@class='tech-category-list']//li/a/text()").getall()])

    @staticmethod
    def _extract_dictionary(data: dict, regex_pattern: str) -> dict:
        """
        Finds the sub dictionary whose keys match regex pattern.

        :param data: the input dict
        :param regex_pattern: regular pattern to match the key
        :return: the sub dictionary whose keys match regex pattern
        """
        result = {}
        for k in data:
            if re.match(regex_pattern, k) is not None:
                result[k] = data[k]
        return result

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: a dict containing the phone and email
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        # for phone number
        for text in response.xpath("//div[@class='information']/ul/li/text()").getall():
            result = extract_phone(text)
            if len(result) > 0:
                contact['phone'] = result[0]
                break
        for text in response.xpath("//div[@class='information']/ul/li/a/@href").getall():
            if text.startswith('mailto:'):
                contact['email'] = text.split(':')[-1]
                break
        return contact
