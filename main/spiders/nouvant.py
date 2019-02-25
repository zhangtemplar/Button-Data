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
from base.util import dictionary_to_markdown, remove_empty_string_from_array
from proxy.pool import POOL


class NouvantSpider(ButtonSpider):
    """
    For crawling data from TTO of school based on Nouvant.com
    """
    name = None
    allowed_domains = []
    start_urls = []
    address = None

    def __init__(self=True):
        super().__init__(True)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                dont_filter=True,
                meta={'proxy': POOL.get()},
                callback=self.parse_list,
                errback=self.handle_failure)

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for row in response.xpath("//div[@id='nouvant-portfolio-content']/div[@class='technology']"):
            title = row.xpath("h2/a/text()").get()
            link = row.xpath("h2/a/@href").get()
            abstract = row.xpath("p/span/text()").get()
            self.log('found patent {}'.format(title), level=logging.INFO)
            patent_links.append({'title': title, 'link': link, 'abstract': abstract})
        statistics = self.statistics(response)
        self.log('found {}/{} patents'.format(statistics['end'], statistics['total']))
        if statistics['end'] < statistics['total']:
            yield response.follow(
                url='/technologies?limit=50&offset={}&query='.format(
                    statistics['end']),
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)
        for p in patent_links:
            name = p['link'].split('/')[-1]
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p['link']), level=logging.INFO)
                continue
            yield response.follow(
                url=p['link'],
                callback=self.parse,
                dont_filter=True,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)

    def statistics(self, response: Response) -> dict:
        data = response.xpath("//div[@id='nouvant-portfolio-content']/div[@class='response']/em/text()").get()
        for m in re.finditer('^([0-9]+)-([0-9]+)[a-zA-Z ]+([0-9]+)', data):
            return {'start': m.group(1), 'end': m.group(2), 'total': m.group(3)}
        return {'start': 0, 'end': 0, 'total': 0}

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

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = response.url.split('/')[-1]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['tag'] = remove_empty_string_from_array(self.add_keywords(response))
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        product['name'] = response.xpath("string(//h1)").get()
        meta = self.get_meta(response)
        contents = meta['abstract'].split('\n')
        if len(contents) > 0 and len(contents[0]) > 0:
            product['abs'] = contents[0]
        else:
            product['abs'] = name
        product['intro'] = '\n'.join(contents[1:])
        del meta['abstract']
        product['asset']['market'] = dictionary_to_markdown(meta)

        manager, product['contact'] = self.get_contact(response)
        product['contact']['website'] = response.url
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for row in response.xpath("//dd[@class='inventor']/a"):
            name = row.xpath("text()").get()
            link = row.xpath("@href").get()
            user = create_user()
            user['name'] = name
            user['ref'] = link
            user['contact']['website'] = link
            user['exp']['exp']['company'] = self.name
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors

    def add_keywords(self, response: Response) -> list:
        """
        Add keywords to the project.

        :param response: Response object
        :return a list of inventors
        """
        return response.xpath("//dd[@class='categories']//li/a/text()").getall()

    def get_contact(self, response: Response) -> (dict, dict):
        """
        Gets the contact information.

        :param response: the response object
        :return: a tuple of two dict, one for an user and the other for the contact information
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}

        # manager
        name = response.xpath("//dd[@class='manager']/a/text()").get()
        link = response.xpath("//dd[@class='manager']/a/@href").get()
        manager = create_user()
        manager['name'] = name
        manager['ref'] = link
        tag = response.xpath("//dd[@class='manager']/div/em[1]/text()").get()
        if tag is not None and isinstance(tag, str):
            manager['tag'] = remove_empty_string_from_array(tag.split(', '))
        contact['phone'] = response.xpath("//dd[@class='manager']/div/em[2]/text()").get()
        manager['contact'] = contact
        manager['contact']['website'] = link
        self.log('find manager {} with contact {}'.format(manager, contact), level=logging.DEBUG)
        return manager, contact

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        title = 'abstract'
        result = {title: ''}
        for row in response.xpath("//div[@class='content']/*"):
            if row.xpath("name()").get() == 'ul':
                result[title] += '\n  - ' + '\n  - '.join(row.xpath("string(li)").getall())
            elif row.xpath("name()").get() == 'h2':
                title = row.xpath("string()").get()
                result[title] = ''
            else:
                # the text content
                result[title] += '\n' + row.xpath("string()").get()
        return result
