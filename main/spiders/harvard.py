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
from base.util import dictionary_to_markdown, extract_dictionary
from proxy.pool import POOL


class HarvardSpider(ButtonSpider):
    name = 'Harvard University'
    allowed_domains = ['otd.harvard.edu']
    start_urls = ['https://otd.harvard.edu/explore-innovation/technologies/results/']
    address = {
        'line1': '1350 Massachusetts Avenue',
        'line2': '',
        'city': 'Cambridge',
        'state': 'MA',
        'zip': '02138',
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
        for link in response.xpath("//h4[@class='result-title']/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        current_page, total_page = self.statictics(response)
        if current_page < total_page:
            self.log('process page {}'.format(self.page), level=logging.INFO)
            yield response.follow(
                url='https://otd.harvard.edu/explore-innovation/technologies/results/P{}/'.format(current_page * 10),
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

    def statictics(self, response: Response) -> (int, int):
        """
        Get the meta data of the patent from the table.

        :return current page, total page
        """
        text = response.xpath('//span[@class="page-current"]/text()').get()
        if text is None:
            return 0, 0
        for m in re.finditer(r'Page ([0-9]+) of ([0-9]+)', text):
            try:
                return int(m.group(1)), int(m.group(2))
            except:
                pass
        return 0, 0

    def parse(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
        name = self.parse_name_from_url(response.url)
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['name'] = response.xpath("string(//h2)").get()
        meta = self.get_meta(response)
        market = extract_dictionary(meta, 'Applications')
        product['asset']['market'] = '\n'.join(market.values())
        summary = extract_dictionary(meta, 'Summary')
        product['intro'] = '\n'.join(summary.values())
        product['abs'] = product['intro'][:product['intro'].find('. ') + 1]
        if len(product['abs']) < 1:
            product['abs'] = product['intro']
        for k in market:
            del meta[k]
        for k in summary:
            del meta[k]
        product['asset']['tech'] = dictionary_to_markdown(meta)
        product['asset']['type'] = 3
        product['addr'] = deepcopy(self.address)
        product['tag'] = self.add_tags(response)
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        contact = self.get_contact(response)
        for index, user in enumerate(contact):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']
        if len(contact) > 0:
            product['contact'] = contact[0]['contact']

        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': product, 'inventors': inventors, 'contact': contact}, fo)

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        title = 'Abstract'
        result = {}
        for row in response.xpath("//article[contains(@class, 'content-main invention-details')]/*"):
            if row.xpath("name()").get() == 'h3':
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
        for row in response.xpath("//div[@class='side-bucket invention-side-block']"):
            if not row.xpath("h4[@class='side-heading']/text()").get() == 'Investigators:':
                continue
            for name in row.xpath("ul/li/text()").getall():
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
        tags = []
        for row in response.xpath("//div[@class='side-bucket invention-side-block']"):
            if not row.xpath("h4[@class='side-heading']/text()").get() == 'Categories:':
                continue
            for name in row.xpath("ul/li/a/text()").getall():
                tags.extend(name.split('/'))
        return tags

    def get_contact(self, response: Response) -> list:
        """
        Gets the contact information.

        :param response: the response object
        :return: a list of contact
        """
        users = []
        for row in response.xpath("//div[@class='associate-item']/div"):
            user = create_user()
            user['ref'] = response.urljoin(row.xpath("a/@href").get())
            user['contact']['website'] = user['ref']
            user['logo'] = response.urljoin(row.xpath("a/img/@src").get())
            user['name'] = row.xpath("h4[@class='team-name']/a/text()").get()
            user['abs'] = row.xpath("strong[@class='team-position']/text()").get()
            user['exp']['exp']['title'] = user['abs']
            user['exp']['exp']['company'] = self.name
            user['contact']['email'] = response.xpath("ul/li[@class='bottom-item bottom-email']/a/@href").get()
            user['contact']['phone'] = response.xpath("ul/li[@class='bottom-item bottom-phone']/a/text()").get()
            users.append(user)
        return users
