# -*- coding: utf-8 -*-
import json
import logging
import os
from copy import deepcopy

from scrapy import Request
from scrapy.http import Response

from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, extract_dictionary, extract_phone
from proxy.pool import POOL


class NewyorkSpider(ButtonSpider):
    name = 'New York University'
    allowed_domains = ['med.nyu.edu']
    start_urls = [
        'https://med.nyu.edu/oil/industry/technologies-licensing/biotechnology',
        'https://med.nyu.edu/oil/industry/technologies-licensing/devices',
        'https://med.nyu.edu/oil/industry/technologies-licensing/diagnostics',
        'https://med.nyu.edu/oil/industry/technologies-licensing/software',
        'https://med.nyu.edu/oil/industry/technologies-licensing/therapeutics']
    address = {
        'line1': 'One Park Avenue',
        'line2': '6th Floor',
        'city': 'New York',
        'state': 'NY',
        'zip': '10016',
        'country': 'USA'}
    item_per_page = 10
    page = 0

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

    def parse_name_from_url(self, url):
        elements = url.split("title=")
        if len(elements) > 1:
            return elements[-1]
        return url.split("/")[-1]

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for link in response.xpath("//ul[@id='tech-licensing']/li/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            if url is None:
                continue
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
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

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = self.parse_name_from_url(response.url)
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['name'] = response.xpath("string(//h1[@class='title'])").get()
        meta = self.get_meta(response)
        market = extract_dictionary(meta, 'Applications')
        product['asset']['market'] = '\n'.join(market.values())
        for k in market:
            del meta[k]
        product['intro'] = dictionary_to_markdown(meta)
        product['abs'] = product['intro'][:product['intro'].find('. ') + 1]
        if len(product['abs']) < 1:
            product['abs'] = product['intro']
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        contact = self.get_contact(response)
        product['contact'] = contact

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        title = 'Abstract'
        result = {}
        skip_first_paragraph = True
        for row in response.xpath("//div[contains(@class,'field field-name-body field-type-text-with-summary')]/div/div/*"):
            if row.xpath("name()").get() == 'h2':
                title = row.xpath("text()").get()
            elif row.xpath("name()").get() == 'p':
                if skip_first_paragraph:
                    skip_first_paragraph = False
                    continue
                result[title] = result.get(title, '') + '\n' + row.xpath("string()").get()
        return result

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for row in response.xpath("//div[contains(@class,'field field-name-body field-type-text-with-summary')]/div/div/p[1]/a"):
            name = row.xpath("text()").get()
            link = row.xpath("@href").get()
            if len(name) < 1:
                continue
            user = create_user()
            user['name'] = name
            user['ref'] = link
            user['contact']['website'] = user['ref']
            user['exp']['exp']['company'] = self.name
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors

    def get_contact(self, response: Response) -> list:
        """
        Gets the contact information.

        :param response: the response object
        :return: a list of contact
        """
        # //div[contains(@class,'field field-name-body field-type-text-with-summary')]/div/div/p[last()]
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        text = response.xpath("string(//div[contains(@class,'field field-name-body field-type-text-with-summary')]/div/div/p[last()])").get()
        phone = extract_phone(text)
        if len(phone) > 0:
            contact['phone'] = phone[0]
        return contact
