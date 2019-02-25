from main.spiders.flintbox import FlintboxSpider
from scrapy import Request
from scrapy.http import Response
import time
import logging
import os
import json
from proxy.pool import POOL
from base.template import create_company
import re
from copy import deepcopy

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

    def parse_school_list(self, response: Response):
        if os.path.exists(os.path.join(self.work_directory, 'links.json')):
            school_links = json.load(open(os.path.join(self.work_directory, 'links.json'), 'r'))
        else:
            driver = self.get_driver(response)
            school_links = []
            while True:
                for row in response.xpath("//table[@id='search-results']/tr"):
                    title = row.xpath("//td[@class='search-results-major']/a/text()")
                    link = row.xpath("//td[@class='search-results-major']/a/@href")
                    school_links.append({'name': title, 'link': link})
                    self.log('find school {}'.format(title), level=logging.INFO)
                stat = self.statistics(response)
                self.log('Finish page {}/{}'.format(stat['current'], stat['total']))
                if stat['current'] < stat['total']:
                    try:
                        next_page = driver.find_element_by_xpath("//img[@class='paginator-next-page paginator-button']")
                        if next_page is not None:
                            next_page.click()
                    except Exception as e:
                        self.log('Fail to go to page {}'.format(stat['current'] + 1), level=logging.ERROR)
                        break
                        pass
                else:
                    break
                time.sleep(3)
            with open(os.path.join(self.work_directory, 'links.json'), 'w') as fo:
                json.dump(school_links, fo)

        for s in school_links:
            yield Request(
                url=s['link'],
                callback=self.parse_list,
                dont_filter=True,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure)

    def statistics(self, response) -> dict:
        """
        Get the statistics from the table.

        :return dict(str, object)
        """
        return {
            'current': int(response.xpath("//input[@name='page_jump']/@value")),
            'total': int(response.xpath("//span[@class='paginator_totalpages_search-results']"))}

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
                meta={'proxy': POOL.get(), 'school': school},
                errback=self.handle_failure)
