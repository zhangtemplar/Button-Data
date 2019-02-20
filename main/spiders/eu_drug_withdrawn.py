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


class EuDrugWithdrawnSpider(EuDrugSpider):
    """
    This class processes the drug approved by Europe Medical Administrative.
    https://www.ema.europa.eu/en/medicines
    """
    name = 'Europe Union Withdrawn Medicine'
    headers = (
        'Category', 'Medicine name', 'Active substance', 'International non-proprietary name (INN) / common name',
        'Therapeutic area', 'Patient safety', 'Orphan medicine', 'Marketing authorisation holder/company name',
        'Type of withdrawal', 'Date of withdrawal', 'Species', 'First published', 'Revision date', 'URL',)

    def __init__(self=True):
        super().__init__(True)
        self.work_directory = os.path.expanduser('~/Downloads/withdrawn/')
        if os.path.exists(os.path.join(self.work_directory, 'withdrawn.json')):
            self.data = json.load(open(os.path.join(self.work_directory, 'withdrawn.json'), 'r'))
        else:
            # process the excel to find the url
            book = load_workbook(
                os.path.expanduser('~/Downloads/Medicines_output_withdrawn_applications.xlsx'))
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
            with open(os.path.join(self.work_directory, 'withdrawn.json'), 'w') as fo:
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
        if code == 'Authorised':
            return 2
        elif code == 'Pending':
            return 1
        elif code == 'Refused' or code == 'Suspended' or code == 'Withdrawn':
            return 3
        else:
            return 3

    def parse(self, response):
        name = response.url.split('/')[-1]
        with open(os.path.join(self.work_directory, name + '.html'), 'wb') as fo:
            fo.write(response.body)
        data = self.data[response.url]
        p = create_product()
        p['name'] = data['Medicine name']
        p['abs'] = data['International non-proprietary name (INN) / common name']
        p['tag'] = [data['Category'] + ' Medicine', 'EU', 'Drug']
        if data['Therapeutic area'] is not None:
            p['tag'].extend(data['Therapeutic area'].split(", "))
        p['website'] = response.url
        p['ref'] = response.url
        if data['Patient safety'] == 'no':
            p['tag'].append('Patient Risk')
        if data['Orphan medicine'] == 'yes':
            p['tag'].append('Orphan medicine')
        if data['Species'] is not None and len(data['Species']) > 0:
            p['tag'].append('Species')
        p['updated'] = data['Revision date']
        p['created'] = data['First published']
        p['asset']['lic'] = p['tag']
        p['asset']['stat'] = 3
        p['asset']['type'] = 1
        p['intro'] = '\n'.join(response.xpath(
            "//div[contains(@class, 'views-field-field-ema-web-summary')]/div/p/text()").getall())
        p['asset']['market'] = dictionary_to_markdown(self.extract_market(response))
        p['asset']['tech'] = dictionary_to_markdown({key: data[key] for key in (
            'Active substance', 'Type of withdrawal', 'Date of withdrawal')})
        p['addr']['city'] = 'Unknown'
        p['addr']['country'] = 'EU'

        a = create_company()
        a['name'] = data['Marketing authorisation holder/company name']
        a['abs'] = 'A Medicine Company'
        a['addr']['city'] = 'Unknown'
        a['addr']['country'] = 'EU'
        a['entr']['bp'] = response.xpath(
            "//div[contains(@class, 'views-field-view-2')]/span/li/a/@href").get()
        with open(os.path.join(self.work_directory, name + '.json'), 'w') as fo:
            json.dump({'product': p, 'applicant': a}, fo)

    @staticmethod
    def extract_market(response: Response) -> dict:
        data = {}
        for field in response.xpath("//div[contains(@class, 'view-ema-questions-and-answers')]/div/dl/dl"):
            key = '\n'.join(field.xpath("dt[@role='heading']/button/text()").getall())
            value = '\n'.join(field.xpath("dd[@role='region']/div/p/text()").getall())
            data[key] = value
        return data
