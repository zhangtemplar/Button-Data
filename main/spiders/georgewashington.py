from main.spiders.nouvant import NouvantSpider


class GeorgeWashingtonSpider(NouvantSpider):
    name = 'George Washington University'
    start_urls = ['http://technologies.research.gwu.edu/technologies']
    address = {
        'line1': '2121 I St NW',
        'line2': '',
        'city': 'Washington',
        'state': 'DC',
        'zip': '20052',
        'country': 'US'}
