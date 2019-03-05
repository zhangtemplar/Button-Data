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
from base.util import dictionary_to_markdown, remove_empty_string_from_array, extract_dictionary
from proxy.pool import POOL


class MitSpider(ButtonSpider):
    name = 'Massachusetts Institute of Technology'
    allowed_domains = ['tlo.mit.edu']
    start_urls = ['http://tlo.mit.edu/explore-mit-technologies/view-technologies']
    address = {
        'line1': '255 Main Street',
        'line2': 'Room NE18-501',
        'city': 'Cambridge',
        'state': 'MA',
        'zip': '02142',
        'country': 'US'}

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
                callback=self.parse_category,
                errback=self.handle_failure)

    def parse_category(self, response: Response):
        # with javascript it would be //div[@class='split-taxonomy-4']/ul/li/a/@href
        for row in response.xpath("//section[@id='block-taxonomy-menu-block-1']/ul/li/a/@href").getall():
            self.log('find category {}'.format(row), level=logging.INFO)
            yield response.follow(
                url=row,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                callback=self.parse_list,
                errback=self.handle_failure)

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for row in response.xpath(
                "//section[@id='block-system-main']/div[@class='node node-technology node-teaser clearfix']/h2/a"):
            name = row.xpath("text()").get()
            link = row.xpath("@href").get()
            patent_links.append({'name': name, 'link': link})
            self.log('found patents {}'.format(name), level=logging.INFO)
        if response.xpath("//li[@class='pager-last']/a/@href").get() is not None and\
                response.url != response.xpath("//li[@class='pager-last']/a/@href").get():
            # have next page
            if '?page=' in response.url:
                elements = response.url.split("=")
                page = (int(elements[-1]) + 1)
                self.log('go to page {}'.format(page), level=logging.INFO)
                yield response.follow(
                    url='='.join(elements[:-1]) + '={}'.format(page),
                    dont_filter=True,
                    meta={'proxy': POOL.get()} if self.with_proxy else {},
                    callback=self.parse_list,
                    errback=self.handle_failure)
            else:
                self.log('go to page 2', level=logging.INFO)
                yield response.follow(
                    url=response.url + '?page=1',
                    dont_filter=True,
                    meta={'proxy': POOL.get()} if self.with_proxy else {},
                    callback=self.parse_list,
                    errback=self.handle_failure)
        for p in patent_links:
            yield response.follow(
                url=p['link'],
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                callback=self.parse,
                errback=self.handle_failure)

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = response.url.split('/')[-1]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['name'] = response.xpath("//h1[@id='page-title']/text()").get()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['addr'] = deepcopy(self.address)
        product['asset']['type'] = 3
        description = self.get_description(response)
        abstract = extract_dictionary(description, 'Applications')
        product['abs'] = '\n'.join(abstract.values())
        if len(product['abs']) < 1:
            product['abs'] = next(iter(description.values()))
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        market = extract_dictionary(description, 'Advantages')
        product['asset']['market'] = '\n'.join(market.values())
        tech = extract_dictionary(description, 'Technology')
        product['asset']['tech'] = '\n'.join(tech.values())
        for k in abstract:
            del description[k]
        for k in market:
            del description[k]
        for k in tech:
            del description[k]
        product['intro'] = dictionary_to_markdown(description)
        product['intro'] = dictionary_to_markdown(description)
        product['tag'] = self.add_keywords(response)
        product['contact'] = self.get_contact(response)

        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            if len(user['abs']) < 1:
                user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']

        patents = self.get_patents(response)
        publications = self.get_publications(response)
        with open(os.path.join(self.work_directory, name + 'json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors, 'patents': patents, 'publications': publications},
                      fo)

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: a dict containing the phone and email
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        contact['email'] = response.xpath("//a[@class='email-tech']/@href").get().split(":")[-1]
        return contact

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for row in response.xpath("//div[contains(@class, 'node-inventor')]"):
            name = row.xpath("string(h2)").get()
            link = 'http://tlo.mit.edu' + row.xpath("h2//a/@href").get()
            department = row.xpath("string(div[@class='content']/div[contains(@class, 'field-name-field-depa')])").get()
            title = row.xpath(
                "string(div[@class='content']/div[contains(@class, 'field-name-field-link-title')])").get()
            user = create_user()
            user['name'] = name
            user['exp']['exp']['company'] = self.name
            user['exp']['exp']['title'] = title
            user['ref'] = link
            user['contact']['website'] = link
            user['abs'] = department
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors

    def get_description(self, response: Response) -> dict:
        """
        Obtain the main information of the patent

        :param response: response
        """
        return {k.xpath("string()").get(): v.xpath("string()").get() for k, v in zip(
            response.xpath("//div[@class='content']/div[contains(@class,'field-name-field-heading')]"),
            response.xpath("//div[@class='content']/div[contains(@class,'field-name-field-body')]"))}

    def add_keywords(self, response: Response) -> list:
        """
        Obtain the keywords of the patent

        :param response: response
        :return list of keywords
        """
        return response.xpath("//ul[@class='term']/li/a/text()").getall()

    def get_patents(self, response: Response) -> list:
        """
        Obtain the patents.

        :param response: response
        :return list of patents
        """
        patents = []
        for row in response.xpath(
                "//div[contains(@class, 'field-collection-item-field-ip-info')]/div[@class='content']"):
            title = row.xpath("string(div[contains(@class, 'field-name-field-ip-title')])").get()
            tag = row.xpath("string(div[contains(@class, 'field-name-field-ip-type')])").get()
            link = row.xpath("div[contains(@class, 'field-name-field-ip-number-pctwo') or contains(@class, 'field-name-field-ip-number-pat-pend')]//a/@href").get()
            patent = create_product()
            patent['asset']['type'] = 1
            patent['ref'] = link if link is not None else ''
            patent['contact']['website'] = link if link is not None else ''
            patent['name'] = title
            patent['tag'] = remove_empty_string_from_array([tag])
        return patents

    def get_publications(self, response: Response) -> list:
        """
        Obtain the patents.

        :param response: response
        :return list of patents
        """
        patents = []
        for row in response.xpath(
                "//div[contains(@class, 'field-collection-item-field-publications')]/div[@class='content']"):
            title = row.xpath("string(div[contains(@class, 'field-name-field-link')])").get()
            other = row.xpath("string(div[contains(@class, 'field-name-field-date-and-other-info')])").get()
            link = row.xpath("div[contains(@class, 'field-name-field-link')]//a/@href").get()
            vendor = row.xpath("string(div[contains(@class, 'field-name-field-publication')])").get()
            patent = create_product()
            patent['asset']['type'] = 8
            patent['ref'] = link
            patent['contact']['website'] = link
            patent['name'] = title
            patent['abs'] = other
            patent['tag'] = remove_empty_string_from_array([vendor])
        return patents
