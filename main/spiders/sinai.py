# -*- coding: utf-8 -*-

from base.util import remove_head_tail_white_space
from main.spiders.inteum import InteumSpider


class SinaiSpider(InteumSpider):
    name = 'Icahn School of Medicine at Mount Sinai'
    allowed_domains = ['msip.technologypublisher.com']
    start_urls = ['http://msip.technologypublisher.com/searchresults.aspx?q=&type=&page=0&sort=datecreated&order=desc']
    address = {
        'line1': '150 East 42nd St',
        'line2': '2nd Floor',
        'city': 'New York',
        'state': 'NY',
        'zip': '10017',
        'country': 'USA'}
    next_page_template = 'http://msip.technologypublisher.com/searchresults.aspx?q=&type=&page={}&sort=datecreated&order=desc'

    def get_meta(self, response):
        result = {}
        title = 'Description'
        for row in response.xpath("//div[@class='c_tp_description']/p"):
            text = remove_head_tail_white_space(row.xpath("string()").get())
            if len(text) < 1:
                continue
            if len(row.xpath(
                    "span[@style=\"font-family: 'Calibri';font-style: Normal;font-size: 16px;color: #376092;\"]")) > 0:
                title = text
            else:
                result[title] = result.get(title, '') + '\n' + text
        return result
