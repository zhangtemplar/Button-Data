import json
import logging
import os
import re
import time
from copy import deepcopy

from scrapy import Request
from scrapy.http import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support.ui import WebDriverWait

from base.template import create_company
from main.spiders.flintbox import FlintboxSpider
from proxy.pool import POOL


class FlintboxAllSpider(FlintboxSpider):
    name = 'Flintbox'
    start_urls = ['https://www.flintbox.com/public/search/?search=Search&objects%3A%3AGroup=1']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'Unknown'}
    blacklist = ['Alberta  Association of Colleges and Technical Institutes', 'C4',
                 'Canadian  Virtual College Consortium', 'Carnegie  Mellon University',
                 "Children's  Hospital Los Angeles", 'Dalhousie  University',
                 'Federal  Partners in Technology Transfer', 'Fuentek', 'Georgetown  University', 'KAUST',
                 'Lawson  Health Research Institute', 'LifeSciences British Columbia', 'McGill  University',
                 'McMaster  University', "Nationwide Children's  Hospital", 'Northwestern  University ',
                 'Oklahoma  State University', 'Parteq  Innovations', 'Rice  University',
                 'Rutgers  University', "St.  Jude Children's Research Hospital",
                 'The  Scripps Research Institute', 'The  University of Kansas',
                 'The  West Coast Licensing Partnership', 'Univalor', 'University  Health Network',
                 'University  of British Columbia', 'University  of Cambridge', 'University  of Guelph',
                 'University  of Iowa', 'University  of Louisville', 'University  of Manitoba',
                 'University  of Massachusetts Lowell', 'University  of Massachusetts Medical School',
                 'University  of Montana', 'University  of North Carolina Charlotte',
                 'University  of Victoria', 'WBT', 'WORLDiscoveries']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                dont_filter=True,
                callback=self.parse_school_list,
                errback=self.handle_failure_selenium)

    def parse_school_list(self, response: Response):
        if os.path.exists(os.path.join(self.work_directory, 'links.json')):
            school_links = json.load(open(os.path.join(self.work_directory, 'links.json'), 'r'))
        else:
            driver = self.get_driver(response)
            school_links = []
            page = 1
            while True:
                for row in driver.find_elements_by_xpath("//table[@id='search-results']/tbody/tr"):
                    title = row.find_element_by_xpath("td[@class='search-results-major']/a").text
                    link = row.find_element_by_xpath("td[@class='search-results-major']/a").get_attribute('href')
                    school_links.append({'name': title, 'link': link})
                    self.log('find school {}'.format(title), level=logging.INFO)
                total_page = self.statistics(response)
                self.log('Finish page {}/{}'.format(page, total_page), level=logging.INFO)
                if page < total_page:
                    try:
                        next_page = driver.find_element_by_xpath("//img[@class='paginator-next-page paginator-button']")
                        if next_page is not None:
                            next_page.click()
                        page += 1
                    except Exception as e:
                        self.log('Fail to go to page {}'.format(page + 1), level=logging.ERROR)
                        break
                else:
                    break
                time.sleep(3)
                wait = WebDriverWait(driver, 30)
                try:
                    wait.until(lambda x: len(x.find_elements_by_xpath("//table[@id='search-results' and @style='opacity: 1;']")) > 0)
                except Exception as e:
                    self.log('Unable to retrieve school information: {}'.format(e), level=logging.ERROR)
                    break
            with open(os.path.join(self.work_directory, 'links.json'), 'w') as fo:
                json.dump(school_links, fo)

        for s in school_links:
            yield Request(
                url=s['link'],
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()} if self.with_proxy else {},
                errback=self.handle_failure)

    def statistics(self, response) -> int:
        """
        Get the statistics from the table.

        :return dict(str, object)
        """
        return int(response.xpath("//span[@class='paginator_totalpages_search-results']/text()").get())

    def get_school_information(self, response: Response) -> dict:
        """
        Get the detailed information for the school.

        :return dict(str, object)
        """
        result = {}
        for row in response.xpath("//table[@summary='Group Details']/tr"):
            key = row.xpath("th/text()").get()
            if key == 'URL':
                value = row.xpath("td/a/@href").get()
            else:
                value = row.xpath("string(td)").get()
            result[key] = value
        return result

    def parse_list(self, response):
        self.log('Parse list {}'.format(response.url), level=logging.INFO)
        name = response.url.split('/')[-1]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        # for the information of school
        school = create_company()
        meta = self.get_school_information(response)
        if 'Name' in meta:
            school['name'] = meta['Name']
        if 'URL' in meta:
            school['ref'] = meta['URL']
            school['contact']['website'] = meta['URL']
        if 'Group Type' in meta:
            school['abs'] = meta['Group Type']
        school['addr'] = deepcopy(self.address)
        school['addr']['line1'] = school['name']
        if school['name'] in self.blacklist:
            return
        patent_links = []
        if os.path.exists(os.path.join(self.work_directory, school['name'] + '.json')):
            patent_links = json.load(open(os.path.join(self.work_directory, school['name'] + '.json'), 'r'))
        else:
            # the id of product is provded in the <script></script>
            for code in response.xpath("//script").getall():
                if 'id_list' in code:
                    ids = re.findall(r'[0-9]+', re.findall(r'\[[0-9,]+\]', code)[0])
                    patent_links = ['https://www.flintbox.com/public/project/{}'.format(patentId) for patentId in ids]
            with open(os.path.join(self.work_directory, school['name'] + '.json'), 'w') as fo:
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
                meta={'proxy': POOL.get(), 'school': school} if self.with_proxy else {'school': school},
                errback=self.handle_failure)
