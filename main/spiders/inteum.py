# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from copy import deepcopy

from dateutil.parser import parse
from scrapy.http import Response
from scrapy import Request

from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, remove_head_tail_white_space, remove_empty_string_from_array, \
    extract_phone, extract_dictionary
from proxy.pool import POOL

class InteumSpider(ButtonSpider):
    """
    Extract the common logic for *.technologypublisher.com, which is provided by Inteum LLC.
    """
    name = None
    allowed_domains = ['technologypublisher.com']
    start_urls = []
    next_page_template = None
    address = None
    item_per_page = 10
    page = 0
    title_xpath = "string(//div[@class='c_content']/table/tr/td/h1)"
    abstract_filter = 'Description|description|Summary'
    market_filter = 'Need|need|Market|market|Value|Application|Advantage'
    tech_filter = 'Technology|Technical'

    def __init__(self, with_proxy: bool=False):
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
        for link in response.xpath('//*[@id="formTechPub1"]/div/table[2]/tr/td/a'):
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
        text = response.xpath('//*[@id="formTechPub1"]/div/table[1]/tr/td[1]/b/text()').get()
        if text is None:
            return 0
        for m in re.finditer(r'([0-9,]+)', text):
            try:
                return int(m.group())
            except:
                pass
        return 0

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
        product['contact']['website'] = response.url
        product['name'] = response.xpath(self.title_xpath).get()
        product['created'] = self.get_disclosure_date(response)
        if product['created'] is None:
            del product['created']
        meta = self.get_meta(response)
        abstract = extract_dictionary(meta, self.abstract_filter)
        product['abs'] = '\n'.join(abstract.values())
        market = extract_dictionary(meta, self.market_filter)
        product['asset']['market'] = '\n'.join(market.values())
        tech = extract_dictionary(meta, self.tech_filter)
        product['asset']['tech'] = '\n'.join(tech.values())
        for k in market:
            del meta[k]
        for k in tech:
            del meta[k]
        for k in abstract:
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
        product['contact'] = self.get_contact(response)

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        result = {}
        title = 'Description'
        for row in response.xpath("//div[@class='c_tp_description']/p"):
            text = remove_head_tail_white_space(row.xpath("string()").get())
            if len(text) < 1:
                continue
            if re.match('^[^:]+:', text) is not None:
                # this is a title
                content = text.split(':')
                if len(content) > 1:
                    title = content[0]
                    content = ':'.join(content[1:])
                    if len(content) > 1:
                        result[title] = content
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
        for row in response.xpath('//*[@id="formTechPub1"]/div/table/tr/td/table[1]/tr/td/a'):
            name = row.xpath("text()").get()
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
        return remove_empty_string_from_array(response.xpath('//*[@id="formTechPub1"]/div/table/tr/td[4]/div[1]/table/tr/td/a/text()').getall())

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: the contact information
        """
        contact = {"website": "", "meet": "", "email": "", "phone": ""}
        email = response.xpath("//div[@class='c_tp_contact']/a/text()").get()
        if email is not None:
            contact['email'] = email
        phone = extract_phone(response.xpath("string(//div[@class='c_tp_contact'])").get())
        if len(phone) > 0:
            contact['phone'] = phone[0]
        return contact
