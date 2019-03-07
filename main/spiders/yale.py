# -*- coding: utf-8 -*-
import json
import logging
import os
from copy import deepcopy

from dateutil.parser import parse
from scrapy import Request
from scrapy.http import Response

from base.buttonspider import ButtonSpider
from base.template import create_product
from base.util import extract_phone
from proxy.pool import POOL


class YaleSpider(ButtonSpider):
    """
    Extract the common logic for *.technologypublisher.com, which is provided by Inteum LLC.
    """
    name = 'Yale University'
    allowed_domains = ['ocr.yale.edu']
    start_urls = ['https://ocr.yale.edu/available-technologies?keys=&field_technology_tags_tid=All']
    address = {
        'line1': '433 Temple Street',
        'line2': '',
        'city': 'New Haven',
        'state': 'CT',
        'zip': '06511',
        'country': 'USA'}
    title_xpath = "string(//h1[@id='page-title'])"

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
        for link in response.xpath("//div[@class='view-content']/div[contains(@class,'views-row')]/div/h3/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        next_page = response.xpath("//li[@class='pager-next']/a/@href").get()
        if next_page is not None:
            self.log('process page {}'.format(next_page), level=logging.INFO)
            yield response.follow(
                url=next_page,
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

    def get_disclosure_date(self, response: Response) -> str or None:
        for text in response.xpath("//div[@id='divDisclosureDate']/text()").getall():
            # Johns Hopkins
            try:
                return parse(text).strftime("%a, %d %b %Y %H:%M:%S GMT")
            except:
                pass
        return None

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = self.parse_name_from_url(response.url)
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['logo'] = response.xpath("//div[contains(@class, 'field-type-image')]//img/@src").get()
        if product['logo'] is None:
            product['logo'] = ''
        product['contact']['website'] = response.url
        product['name'] = response.xpath(self.title_xpath).get()
        product['created'] = self.get_disclosure_date(response)
        if product['created'] is None:
            del product['created']
        product['intro'] = response.xpath(
            "string(//div[@class='field field-name-body field-type-text-with-summary field-label-above']/div[@class='field-items'])").get()
        product['abs'] = product['intro'][:product['intro'].find('. ') + 1]
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        product['contact'] = self.get_contact(response)
        patents = self.add_patents(response)
        for p in patents:
            p['addr'] = product['addr']
            p['contact'] = product['contact']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'patent': patents}, fo)

    def add_patents(self, response: Response) -> list:
        """
        Add patents to the project.

        :param response: Response object
        :return a list of inventors
        """
        result = []
        for row in response.xpath(
                "//div[@class='field field-name-field-patent field-type-link-field field-label-above']/div[@class='field-items']//a"):
            patent = create_product()
            patent['name'] = row.xpath("text()").get()
            patent['ref'] = row.xpath("@href").get()
            patent['contact']['website'] = patent['ref']
            patent['asset']['type'] = 1
            patent['abs'] = patent['name']
            result.append(patent)
        return result

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: the contact information
        """
        contact = {"website": "", "meet": "", "email": "", "phone": ""}
        email = response.xpath(
            "//div[@class='field field-name-field-contact-manager field-type-entityreference field-label-above']/div[@class='field-items']//a/@href").get().split(
            ":")[-1]
        if email is not None:
            contact['email'] = email
        phone = extract_phone(response.xpath(
            "string(//div[@class='field field-name-field-contact-manager field-type-entityreference field-label-above']/div[@class='field-items'])").get())
        if len(phone) > 0:
            contact['phone'] = phone[0]
        return contact
