from main.spiders.nouvant import NouvantSpider


class UcfSpider(NouvantSpider):
    name = 'University of Central Florida'
    start_urls = ['http://technologies.tt.research.ucf.edu/technologies']
    address = {
        'line1': '4000 Central Florida Blvd',
        'line2': '',
        'city': 'Orlando',
        'state': 'FL',
        'zip': '32816',
        'country': 'US'}
