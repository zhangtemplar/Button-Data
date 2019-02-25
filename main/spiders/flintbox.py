# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from copy import deepcopy
from typing import Iterable, List

from dateutil.parser import parse
from scrapy import Request
from scrapy.http import Response
from scrapy.selector import Selector

from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, extract_phone
from proxy.pool import POOL


class FlintboxSpider(ButtonSpider):
    name = None
    allowed_domains = ['flintbox.com']
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
        if os.path.exists(os.path.join(self.work_directory, 'links.json')):
            patent_links = json.load(open(os.path.join(self.work_directory, 'links.json'), 'r'))
        else:
            # the id of product is provded in the <script></script>
            for code in response.xpath("//script").getall():
                if 'id_list' in code:
                    ids = re.findall(r'[0-9]+', re.findall(r'\[[0-9,]+\]', code)[0])
                    patent_links = [response.url + '/public/project/{}'.format(patentId) for patentId in ids]
            with open(os.path.join(self.work_directory, 'links.json'), 'w') as fo:
                json.dump(patent_links, fo)
        for p in patent_links:
            name = p.split('/')[-1]
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield response.follow(
                url=p,
                callback=self.parse,
                dont_filter=True,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)

    def get_name(self, response: Response):
        if response is not None and 'school' in response.request.meta and 'name' in response.request.meta['school']\
                and len(response.request.meta['school']['name']) > 0:
            return response.request.meta['school']['name']
        else:
            return self.name

    def get_address(self, response: Response):
        if response is not None and 'school' in response.request.meta and 'addr' in response.request.meta['school']:
            return response.request.meta['school']['addr']
        else:
            return self.address

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
        product['contact']['website'] = response.url
        meta = self.get_meta(response)
        product['name'] = meta['Project Title']
        try:
            product['created'] = parse(meta['Posted Date']).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        product['tag'] = meta['Tags']
        if len(meta['banner']) > 0:
            product['logo'] = meta['banner'][0]
        product['asset']['type'] = 3
        abstract = self._extract_dictionary(meta, 'brief|Brief|BRIEF|Short')
        product['abs'] = '\n'.join(abstract.values())
        if len(product['abs']) < 1:
            product['abs'] = next(iter(meta.values()))
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        introduction = self._extract_dictionary(meta, 'abstract|Abstract')
        product['intro'] = '\n'.join(introduction.values())
        for k in abstract:
            del meta[k]
        for k in introduction:
            del meta[k]
        product['asset']['market'] = dictionary_to_markdown(meta)
        product['contact'] = self.get_contact(response)
        product['addr'] = deepcopy(self.get_address(response))
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        result = {}
        # Note: if running with JS, the data can be found in //div[@id='dynamic_content']/table[2]/tbody/tr
        for row in response.xpath("//div[@id='dynamic_content']/table/table/tr"):
            try:
                title = row.xpath("string(th)").get()
            except Exception as e:
                self.log('Fail to find title for meta', level=logging.WARN)
                continue
            if len(title) < 1:
                continue
            result[title] = ''
            for line in row.xpath('td/*'):
                tag = line.xpath('name()').get()
                if tag.startswith('ul'):
                    # it is a list, keep it in markdown format
                    if len(result[title]) > 0:
                        result[title] += '\n'
                    result[title] += '  - '
                    result[title] += '\n  - '.join(line.xpath("li").xpath('string()').getall())
                else:
                    # anything else, e.g., a paragraph
                    if len(result[title]) > 0:
                        result[title] += '\n'
                    result[title] += line.xpath('string()').get()
            if len(row.xpath('td/*')) < 1:
                if len(result[title]) > 0:
                    result[title] += '\n'
                result[title] += row.xpath('string(td)').get()
            if 'Tags' in title:
                result[title] = row.xpath('td/a/text()').getall()
            elif 'Abstract' in title:
                result['banner'] = self.get_pictures(row.xpath('td'))
        return result

    def get_pictures(self, contents: Iterable[Selector]) -> List[str]:
        """
        Get the picture urls from the webelement.

        :param contents: the webelements which may contain picture urls
        :return: the picture urls
        """
        links = []
        for content in contents:
            for picture in content.xpath("//img/@src").getall():
                if len(picture) >= 256:
                    continue
                links.append(picture)
        return links

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: a dict containing the phone and email
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        contact_title_found = False
        for row in response.xpath("//div[@id='dynamic_content']/div[@class='subhead' or contains(@id, 'textelement')]"):
            if contact_title_found:
                phone = extract_phone(row.xpath('string()').get())
                if len(phone) > 0:
                    contact['phone'] = phone[0]
                email = row.xpath('//a/@href').split(':')
                if len(email) > 1:
                    contact['email'] = email[1]
                self.log('Found contact {}'.format(contact), level=logging.DEBUG)
                break
            if 'Licensing Contact' in row.xpath('string()').get():
                contact_title_found = True
        return contact

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        inventor_found = False
        for row in response.xpath("//div[@id='alt_toolbox']/*"):
            if inventor_found:
                for name in row.xpath('li/text()').getall():
                    if len(name) < 1:
                        continue
                    user = create_user()
                    user['name'] = name
                    user['exp']['exp']['company'] = self.get_name(response)
                    inventors.append(user)
                    self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
                break
            if row.xpath('name()').get() == 'h2' and row.xpath('string()').get() == 'Researchers':
                inventor_found = True
        return inventors
