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
from dateutil.parser import parse

class EmorySpider(ButtonSpider):
    name = 'Emory University'
    allowed_domains = ['olv.duke.edu']
    start_urls = ['http://emoryott.technologypublisher.com/searchresults.aspx?q=&type=&page=0&sort=datecreated&order=desc']
    address = {
        'line1': '201 Dowman Drive',
        'line2': '',
        'city': 'Atlanta',
        'state': 'GA',
        'zip': '30322',
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
        for link in response.xpath("//table/tr/td/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        self.page += 1
        if self.page * self.item_per_page < self.statictics(response):
            self.log('process page {}'.format(self.page), level=logging.INFO)
            yield response.follow(
                url='http://emoryott.technologypublisher.com/searchresults.aspx?q=&type=&page={}&sort=datecreated&order=desc'.format(self.page),
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

        :return dict(str, object)
        """
        for text in response.xpath('//td[@valign="top"]/b/text()').getall():
            try:
                return int(text)
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
        product['name'] = response.xpath("string(//table/tr/td/h1)").get()
        meta = self.get_meta(response)
        abstract = self._extract_dictionary(meta, 'Application|Abstract')
        product['abs'] = '\n'.join(abstract.values())
        if len(product['abs']) < 1:
            product['abs'] = next(iter(meta.values()))
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        market = self._extract_dictionary(meta, 'Market')
        product['asset']['market'] = '\n'.join(market.values())
        tech = self._extract_dictionary(meta, 'Technical')
        product['asset']['tech'] = '\n'.join(tech.values())
        for k in abstract:
            del meta[k]
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
        product['contact'] = self.get_contact(response)
        try:
            product['created'] = parse(response.xpath("//div[@id='divWebPublished']/font/text()").get()).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except Exception as e:
            self.log("fail to obtain creation date {}".format(e), level=logging.ERROR)

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        title = 'Abstract'
        result = {title: ''}
        for row in response.xpath("//div[@class='c_tp_description']/*"):
            if row.xpath("name()").get() == 'h5':
                title = row.xpath("text()").get()
            elif row.xpath("name()").get() == 'ul':
                result[title] = result.get(title, '') + '\n  - ' + '\n  - '.join(row.xpath("string(li)").getall())
            elif row.xpath("name()").get() == 'p':
                result[title] = result.get(title, '') + '\n' + row.xpath("string()").get()
        return result

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for row in response.xpath("//td/table/tr/td/a"):
            link = row.xpath('@href').get()
            if not link.startswith('/bio.aspx?id='):
                continue
            name = row.xpath("text()").get()
            if len(name) < 1:
                continue
            user = create_user()
            user['name'] = name
            user['ref'] = link
            user['contact']['website'] = link
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
        tags = []
        for row in response.xpath("//td/table/tr/td/a"):
            link = row.xpath('@href').get()
            if not link.startswith('/searchresults.aspx?q='):
                continue
            name = row.xpath("text()").get()
            if len(name) < 1:
                continue
            tags.append(name)
        return tags

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
        for result in response.xpath('string(//*[@id="formTechPub1"]/div/table/tr/td[3])').getall():
            phone = extract_phone(result)
            if len(phone) > 0:
                contact['phone'] = phone[0]
        for text in response.xpath('//*[@id="formTechPub1"]/div/table/tr/td[3]//a/@href').getall():
            if text.startswith('mailto:'):
                contact['email'] = text.split(':')[-1]
                break
        return contact
