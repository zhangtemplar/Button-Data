# -*- coding: utf-8 -*-
import logging

from dateutil.parser import parse
from scrapy.http import Response

from base.template import create_user
from base.util import extract_phone
from main.spiders.inteum import InteumSpider


class EmorySpider(InteumSpider):
    name = 'Emory University'
    allowed_domains = ['emoryott.technologypublisher.com']
    start_urls = [
        'http://emoryott.technologypublisher.com/searchresults.aspx?q=&type=&page=0&sort=datecreated&order=desc']
    address = {
        'line1': '201 Dowman Drive',
        'line2': '',
        'city': 'Atlanta',
        'state': 'GA',
        'zip': '30322',
        'country': 'USA'}
    next_page_template = 'http://emoryott.technologypublisher.com/searchresults.aspx?q=&type=&page={}&sort=datecreated&order=desc'
    title_xpath = "string(//table/tr/td/h1)"
    abstract_filter = 'Application|Abstract'
    market_filter = 'Need|need|Market|market|Value|Advantage'

    def get_disclosure_date(self, response: Response):
        try:
            return parse(response.xpath("//div[@id='divWebPublished']/font/text()").get()).strftime(
                "%a, %d %b %Y %H:%M:%S GMT")
        except:
            return None

    tech_filter = 'Technology|Technical'

    def get_meta(self, response: Response) -> dict:
        """
        Get the meta data of the patent from the table.

        :return dict(str, object)
        """
        title = 'Abstract'
        result = {title: ''}
        for row in response.xpath("//div[@class='c_tp_description']/*"):
            if row.xpath("name()").get() == 'h5':
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
        for row in response.xpath('//*[@id="formTechPub1"]/div/table/tr/td/table[2]/tr/td/a'):
            name = row.xpath("text()").get()
            link = row.xpath("@href").get()
            if len(name) < 1:
                continue
            user = create_user()
            user['name'] = name
            user['ref'] = link
            user['contact']['website'] = link
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
        for row in response.xpath("//td/table/tr/td/a"):
            link = row.xpath('@href').get()
            if not link.startswith('/searchresults.aspx?q='):
                continue
            name = row.xpath("text()").get()
            if len(name) < 1:
                continue
            tags.append(name)
        return tags

    def get_contact(self, response: Response) -> dict:
        """
        Gets the contact information.

        :param response: the response object
        :return: a dict containing the phone and email
        """
        contact = {'email': '', 'phone': '', 'website': response.url, 'meet': ''}
        for result in response.xpath('string(//*[@id="formTechPub1"]/div/table/tr/td[3])').getall():
            phone = extract_phone(result)
            if len(phone) > 0:
                contact['phone'] = phone[0]
        for text in response.xpath('//*[@id="formTechPub1"]/div/table/tr/td[3]//a/@href').getall():
            if text.startswith('mailto:'):
                contact['email'] = text.split(':')[-1]
                break
        return contact
