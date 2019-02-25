from main.spiders.nouvant import NouvantSpider


class GatechSpider(NouvantSpider):
    name = 'Georgia Institute of Technology'
    start_urls = ['http://technologies.gtrc.gatech.edu/technologies']
    address = {
        'line1': 'North Ave NW',
        'line2': '',
        'city': 'Atlanta',
        'state': 'GA',
        'zip': '30332',
        'country': 'US'}
