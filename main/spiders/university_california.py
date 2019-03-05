# -*- coding: utf-8 -*-
import json
import logging
import os
import re
import time
from copy import deepcopy

from dateutil.parser import parse
from scrapy import Request
from scrapy.http import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from base.buttonspider import ButtonSpider
from base.template import create_product, create_user
from base.util import dictionary_to_markdown, extract_phone, extract_dictionary
from proxy.pool import POOL


class UniversityCaliforniaSpider(ButtonSpider):
    name = None
    allowed_domains = ['techtransfer.universityofcalifornia.edu']
    start_urls = []
    address = None

    def __init__(self):
        super().__init__(False)
        self.work_directory = os.path.expanduser('~/Downloads/{}'.format(self.name))
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory)

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_list,
                errback=self.handle_failure_selenium)

    def parse_list(self, response: Response):
        driver = self.get_driver(response)
        # wait for page to load
        # wait for the redirect to finish.
        patent_links = []
        if os.path.exists(os.path.join(self.work_directory, 'links.json')):
            patent_links = json.load(open(os.path.join(self.work_directory, 'links.json'), 'r'))
        else:
            while True:
                time.sleep(1)
                self.wait_for_element(driver, "//div[@id='ctl00_ContentPlaceHolder1_UpdateProgress1' and @style='display: block;']")
                table = driver.find_element_by_xpath("//div[@class='table-body']")
                for r in table.find_elements_by_xpath("div"):
                    cols = r.find_elements_by_xpath("div")
                    patent = cols[2].find_element_by_xpath('p/a')
                    abstract = cols[2].find_element_by_xpath('div/p')
                    patent_links.append({'name': patent.text, 'link': patent.get_attribute('href'), 'abstract': abstract.text})
                    self.log('Found technology {}'.format(patent.text), level=logging.INFO)
                if not self.next_page(driver):
                    break
                time.sleep(3)
            with open(os.path.join(self.work_directory, 'links.json'), 'w') as fo:
                json.dump(patent_links, fo)
        for p in patent_links:
            name = p['link'].split('/')[-1]
            if os.path.exists(os.path.join(self.work_directory, name[:-4] + 'json')):
                self.log('{} already parsed and will skip'.format(p['link']), level=logging.INFO)
                continue
            yield Request(
                url=p['link'],
                callback=self.parse,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)

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
        with open(os.path.join(self.work_directory, name), 'wb') as fo:
            fo.write(response.body)
        product = create_product()
        product['name'] = response.xpath("//h1[@class='tech-heading tech-heading-main']/text()").get()
        product['ref'] = response.url
        product['contact']['website'] = response.url
        product['addr'] = deepcopy(self.address)
        product['asset']['type'] = 3
        description = self.get_description(response)
        abstract = extract_dictionary(description, 'brief|Brief|BRIEF')
        product['abs'] = '\n'.join(abstract.values())
        if len(product['abs']) < 1:
            product['abs'] = next(iter(description.values()))
        if len(product['abs']) < 1:
            product['abs'] = product['name']
        introduction = extract_dictionary(description, 'full|Full|FULL')
        product['intro'] = '\n'.join(introduction.values())
        for k in abstract:
            del description[k]
        for k in introduction:
            del description[k]
        product['asset']['market'] = dictionary_to_markdown(description)
        product['contact'] = self.get_contact(response)
        product['tag'] = self.add_keywords(response)

        contact_person = self.get_contact_person(response)
        contact_person['abs'] = 'Person of Contact for ' + product['name']
        contact_person['addr'] = product['addr']
        contact_person['contact'] = product['contact']
        contact_person['tag'] = product['tag']
        inventors = self.add_inventors(response)
        for index, user in enumerate(inventors):
            user['abs'] = 'Inventor of ' + product['name']
            user['addr'] = product['addr']
            user['tag'] = product['tag']

        patents = self.get_patents(response)
        with open(os.path.join(self.work_directory, name[:-4] + 'json'), 'w') as fo:
            json.dump({'product': product, 'contact': contact_person, 'inventors': inventors, 'patents': patents}, fo)


    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: a dict containing the phone and email
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        contact['email'] = response.xpath("string(//*[@id='email'])").get()
        phone = extract_phone(response.xpath("//*[@id='PhoneNumber']/@onclick").get())
        if len(phone) > 0:
            contact['phone'] = phone[0]
        self.log('Found contact {}'.format(contact), level=logging.DEBUG)
        return contact

    def get_contact_person(self, response: Response) -> dict:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        user = create_user()
        user['name'] = response.xpath("string(//*[@id='contact-person'])").get()
        user['exp']['exp']['company'] = self.name
        self.log('Found contact person {}'.format(user['name']), level=logging.DEBUG)
        return user

    def add_inventors(self, response: Response) -> list:
        """
        Add inventors to the project.

        :param response: Response object
        :return a list of inventors
        """
        inventors = []
        for name in response.xpath("//div[@class='ncd-data inventors display-block indented']/ul/li/text()").getall():
            if len(name) < 1:
                continue
            user = create_user()
            user['name'] = name
            user['exp']['exp']['company'] = self.name
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors

    def get_description(self, response: Response) -> dict:
        """
        Obtain the main information of the patent

        :param response: response
        """
        result = {}
        title = None
        for row in response.xpath("//div[@class='ncd-data fields display-block indented']/*"):
            tag = row.xpath('name()').get()
            if tag.startswith('h'):
                # it is a title
                title = row.xpath('string()').get()
                result[title] = ''
            elif tag.startswith('ul'):
                # it is a list, keep it in markdown format
                if len(result[title]) > 0:
                    result[title] += '\n'
                result[title] += '  - '
                result[title] += '\n  - '.join(row.xpath("li").xpath('string()').getall())
            else:
                # anything else, e.g., a paragraph
                if len(result[title]) > 0:
                    result[title] += '\n'
                result[title] += row.xpath('string()').get()
        return result

    def add_keywords(self, response: Response) -> list:
        """
        Obtain the keywords of the patent

        :param response: response
        :return list of keywords
        """
        categories = response.xpath(
            "//div[@class='ncd-data otherdata-categories display-block indented ']//a/text()").getall()
        try:
            # keyword may not exist
            categories.extend(response.xpath("//div[@class='ncd-data otherdata-keywords']/p/text()").get().split(', '))
        except:
            pass
        return categories

    def get_patents(self, response: Response) -> list:
        """
        Obtain the patents.

        :param response: response
        :return list of patents
        """
        patents = []
        for row in response.xpath("//tr[@class='patentRow']"):
            patent = create_product()
            patent['asset']['type'] = 1
            patent['asset']['status'] = 1 if re.match(
                'issued|approved', row.xpath("//td[2]/text()").get(), re.IGNORECASE) is None else 2
            patent['ref'] = row.xpath("//td[3]/a/@href").get()
            patent['name'] = row.xpath("//td[3]/a/text()").get()
            try:
                patent['created'] = parse(row.xpath["//td[4]"]).strftime("%a, %d %b %Y %H:%M:%S GMT")
            except:
                pass
        return patents


    def wait_for_element(self, driver: WebDriver, xpath: str, timeout: int=30) -> bool:
        wait = WebDriverWait(driver, timeout)
        try:
            wait.until(lambda x: len(x.find_elements_by_xpath(xpath)) < 1)
            return True
        except:
            self.log('Timeout will waiting for page to load', level=logging.ERROR)
            return False


    def next_page(self, driver: WebDriver) -> bool:
        """
        Click to get to next page.

        :return: true, if next page button is clicked
        """
        current_page = int(
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_ucNCDList_ucPagination_lblCurrentPageNum').text)
        total_page = int(
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_ucNCDList_ucPagination_lblTotalPages').text)
        self.log('finish page {}/{}'.format(current_page, total_page), level=logging.INFO)
        if current_page >= total_page:
            return False
        while True:
            try:
                button = driver.find_element_by_xpath("//li[@class='next']") \
                    .find_element_by_xpath('a') \
                    .find_element_by_xpath('i')
                if button is not None:
                    button.click()
                    return True
            except Exception as e:
                self.log(e, level=logging.ERROR)
                time.sleep(5)
        return False
