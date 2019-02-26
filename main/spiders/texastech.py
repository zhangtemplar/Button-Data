import logging

from base.template import create_user
from main.spiders.nouvant import NouvantSpider


class TexasTechSpider(NouvantSpider):
    name = 'Texas Tech University'
    start_urls = ['http://technologies.texastech.edu/technologies']
    address = {
        'line1': '2500 Broadway',
        'line2': '',
        'city': 'Lubbock',
        'state': 'TX',
        'zip': '79409',
        'country': 'US'}

    def add_inventors(self, response):
        inventors = []
        for row in response.xpath("//dd[@class='inventor']"):
            name = row.xpath("a/text()").get()
            link = row.xpath("a/@href").get()
            abstract = row.xpath('string(div[1])').get()
            user = create_user()
            user['name'] = name
            user['abs'] = abstract
            user['ref'] = link
            user['contact']['website'] = link
            user['exp']['exp']['company'] = self.name
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors
