import logging

from base.template import create_user
from main.spiders.texastech import NouvantSpider


class UncSpider(NouvantSpider):
    name = 'University of North Carolina—​Chapel Hill'
    start_urls = ['http://technologies.unc.edu/technologies']
    address = {
        'line1': '153A Country Club Road',
        'line2': '',
        'city': 'Chapel Hill',
        'state': 'NC',
        'zip': '27514',
        'country': 'US'}

    def add_inventors(self, response):
        inventors = []
        for row in response.xpath("//dd[@class='inventor']"):
            name = row.xpath("a/text()").get()
            link = row.xpath("a/@href").get()
            abstract = row.xpath('string(div[1])').get().split(', ')
            user = create_user()
            user['name'] = name
            user['abs'] = ', '.join(abstract[1:])
            user['ref'] = link
            user['contact']['website'] = link
            user['exp']['exp']['company'] = self.name
            user['exp']['exp']['title'] = abstract[0] if len(abstract) > 0 else ''
            inventors.append(user)
            self.log('Found inventor {}'.format(user['name']), level=logging.DEBUG)
        return inventors
