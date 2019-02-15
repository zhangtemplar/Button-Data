# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from openpyxl import load_workbook
from scrapy import Request
from scrapy.http.response import Response

from base.template import create_product, create_company
from base.util import dictionary_to_markdown
from main.spiders.eu_drug import EuDrugSpider
from proxy.pool import POOL


class EuDrugHerbalSpider(EuDrugSpider):
    """
    This class processes the drug approved by Europe Medical Administrative.
    https://www.ema.europa.eu/en/medicines
    """
    name = 'Europe Union Approved Medicine'
    headers = (
        'Status', 'Latin name of herbal substance', 'Botanical name of plant',
        'English common name of herbal substance', 'Combination', 'Use', 'Outcome', 'Date added to the inventory',
        'Date added to the priority list', 'First published', 'Revision date', 'URL',)

    def __init__(self):
        super().__init__(True)
        self.work_directory = os.path.expanduser('~/Downloads/herbal/')
        if os.path.exists(os.path.join(self.work_directory, 'herbal.json')):
            self.data = json.load(open(os.path.join(self.work_directory, 'herbal.json'), 'r'))
        else:
            # process the excel to find the url
            book = load_workbook(
                os.path.expanduser('~/Downloads/Medicines_output_herbal_medicines.xlsx'))
            sheet = book.get_sheet_by_name('Worksheet 1')
            self.data = {}
            for index, row in enumerate(sheet.rows):
                if index <= self.rows_to_skip:
                    continue
                columns = {}
                for key, value in zip(self.headers, row):
                    if value.value is None:
                        columns[key] = ''
                    elif isinstance(value.value, datetime):
                        columns[key] = value.value.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    else:
                        columns[key] = value.value
                self.data[columns['URL']] = columns
            with open(os.path.join(self.work_directory, 'herbal.json'), 'w') as fo:
                json.dump(self.data, fo)

    def start_requests(self):
        for url in self.data.keys():
            if url is None or not url.startswith('http'):
                continue
            name = url.split('/')[-1]
            if os.path.exists(os.path.join(self.work_directory, name + '.json')):
                continue
            yield Request(
                url=url,
                meta={'proxy': POOL.get()},
                errback=self.handle_failure,
                callback=self.parse)

    @staticmethod
    def status_code(code):
        if code.startswith('F') or code.startswith('P'):
            return 2
        elif code.startswith('C') or code.startswith('D'):
            return 1
        else:
            return 1

    def parse(self, response):
        name = response.url.split('/')[-1]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        data = self.data[response.url]
        p = create_product()
        p['name'] = data['English common name of herbal substance']
        p['abs'] = data['Botanical name of plant']
        p['tag'] = ["EU", 'Drug', 'Herbal']
        if data['Use'] is not None:
            p['tag'].extend(data['Use'].split(', '))
        p['website'] = response.url
        p['ref'] = response.url
        if data['Combination'] == 'yes':
            p['tag'].append('Combination')
        p['asset']['stat'] = self.status_code(data['Status'])
        p['asset']['tech'] = dictionary_to_markdown({key: data[key] for key in (
            'Latin name of herbal substance', 'Outcome', 'Date added to the inventory',
            'Date added to the priority list',	'First published',	'Revision date')})
        p['updated'] = data['Revision date']
        p['created'] = data['First published']
        p['asset']['lic'] = p['tag']
        p['asset']['type'] = 1
        p['intro'] = '\n'.join(response.xpath(
            "//div[contains(@class, 'field-name-field-ema-web-summary')]/div/div/p/text()").getall())
        p['asset']['market'] = dictionary_to_markdown(self.extract_market(response))
        p['addr']['city'] = 'Unknown'
        p['addr']['country'] = 'EU'
        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump(p, fo)

    @staticmethod
    def extract_market(response: Response) -> dict:
        data = {}
        for field in response.xpath("//div[contains(@class, 'group-ema-overview')]/dl/dl"):
            key = '\n'.join(field.xpath("dt[@role='heading']/button/text()").getall())
            value = '\n'.join(field.xpath("dd[@role='region']/div/p/text()").getall())
            data[key] = value
        return data
