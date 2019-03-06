# -*- coding: utf-8 -*-

from main.spiders.inteum import InteumSpider


class PennsylvaniaSpider(InteumSpider):
    name = 'University of Pennsylvania'
    allowed_domains = ['upenn.technologypublisher.com']
    start_urls = ['http://upenn.technologypublisher.com/searchresults.aspx']
    address = {
        'line1': '3160 Chestnut Street  ',
        'line2': 'Suite 200',
        'city': 'Philadelphia',
        'state': 'PA',
        'zip': '19104',
        'country': 'USA'}
    next_page_template = 'http://upenn.technologypublisher.com/searchresults.aspx?q=&type=&page={}&sort=datecreated&order=desc'
