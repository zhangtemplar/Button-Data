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
    blacklist = ['Alberta\r\n  Association of Colleges and Technical Institutes', 'C4',
                 'Canadian\r\n  Virtual College Consortium', 'Carnegie\r\n  Mellon University',
                 "Children's\r\n  Hospital Los Angeles", 'Dalhousie\r\n  University',
                 'Federal\r\n  Partners in Technology Transfer', 'Fuentek', 'Georgetown\r\n  University', 'KAUST',
                 'Lawson\r\n  Health Research Institute', 'LifeSciences British Columbia', 'McGill\r\n  University',
                 'McMaster\r\n  University', "Nationwide Children's\r\n  Hospital", 'Northwestern\r\n  University ',
                 'Oklahoma\r\n  State University', 'Parteq\r\n  Innovations', 'Rice\r\n  University',
                 'Rutgers\r\n  University', "St.\r\n  Jude Children's Research Hospital",
                 'The\r\n  Scripps Research Institute', 'The\r\n  University of Kansas',
                 'The\r\n  West Coast Licensing Partnership', 'Univalor', 'University\r\n  Health Network',
                 'University\r\n  of British Columbia', 'University\r\n  of Cambridge', 'University\r\n  of Guelph',
                 'University\r\n  of Iowa', 'University\r\n  of Louisville', 'University\r\n  of Manitoba',
                 'University\r\n  of Massachusetts Lowell', 'University\r\n  of Massachusetts Medical School',
                 'University\r\n  of Montana', 'University\r\n  of North Carolina Charlotte',
                 'University\r\n  of Victoria', 'WBT', 'WORLDiscoveries']

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
                for row in response.xpath("//table[@id='search-results']/tbody/tr"):
                    title = row.xpath("//td[@class='search-results-major']/a/text()").get()
                    link = row.xpath("//td[@class='search-results-major']/a/@href").get()
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
                value = row.xpath("string(th)").get()
            result[key] = value
        return result

    def parse_list(self, response):
        self.log('Parse technology {}'.format(response.url), level=logging.INFO)
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
                meta={'proxy': POOL.get(), 'school': school} if self.with_proxy else {'school': school},
                errback=self.handle_failure)
