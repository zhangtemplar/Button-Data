# -*- coding: utf-8 -*-
import logging
import os
import re

from scrapy.http import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from base.template import create_user
from base.util import remove_empty_string_from_array
from main.spiders.inteum import InteumSpider


class JohnsHopkinsSpider(InteumSpider):
    name = 'JohnsHopkins University'
    allowed_domains = ['jhu.technologypublisher.com']
    start_urls = ['http://jhu.technologypublisher.com/']
    address = {
        'line1': '1812 Ashland Avenue',
        'line2': 'Suite 110',
        'city': 'Baltimore',
        'state': 'MD',
        'zip': '21205',
        'country': 'USA'}
    title_xpath = "string(//h1)"
    market_filter = 'Need|need|Market|market|Value|Application|Advantage|novelty'

    def __init__(self, with_proxy: bool = False):
        super().__init__(with_proxy)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_list,
                wait_time=30,
                wait_until=expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@id='hits-container']/div")),
                errback=self.handle_failure_selenium)

    def parse_name_from_url(self, url):
        elements = url.split("title=")
        if len(elements) > 1:
            return elements[-1]
        return url.split("/")[-1]

    def parse_list(self, response: Response):
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        for link in response.xpath("//div[@class='hit-content']/a"):
            text = link.xpath("text()").get()
            url = link.xpath("@href").get()
            self.log("find technology {}/{}".format(text, url), level=logging.INFO)
            patent_links.append(url)
        # for next page
        total_result = self.statictics(response)
        self.page += 1
        if self.page * self.item_per_page < total_result:
            self.log('process page {}'.format(self.page), level=logging.INFO)
            yield SeleniumRequest(
                url='http://jhu.technologypublisher.com/?q=&hPP=20&idx=Prod_Inteum_TechnologyPublisher_jhu&p={}'.format(
                    self.page),
                dont_filter=True,
                wait_time=30,
                callback=self.parse_list,
                wait_until=expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='hit-content']/a")),
                errback=self.handle_failure_selenium)
        for p in patent_links:
            name = self.parse_name_from_url(p)
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                self.log('{} already parsed and will skip'.format(p), level=logging.INFO)
                continue
            yield SeleniumRequest(
                url=p,
                callback=self.parse,
                dont_filter=True,
                wait_time=30,
                errback=self.handle_failure_selenium)

    def statictics(self, response: Response) -> int:
        """
        Get the meta data of the patent from the table.

        :return total result
        """
        text = response.xpath('//div[@class="ais-body ais-stats--body"]/div/text()').get()
        if text is None:
            return 0
        for m in re.finditer(r'([0-9,]+)', text):
            try:
                return int(m.group().replace(',', ''))
            except:
                pass
        return 0

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for name in response.xpath("//div[@id='inventorLinks']/div/a/text()").getall():
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
        return remove_empty_string_from_array(response.xpath("//div[@id='categoryLinks']/div/a/text()").getall())
