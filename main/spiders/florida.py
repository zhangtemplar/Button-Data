from main.spiders.nouvant import NouvantSpider


class FloridaSpider(NouvantSpider):
    name = 'University of Florida'
    start_urls = ['http://technologylicensing.research.ufl.edu/technologies']
    address = {
        'line1': '201 Criser Hall',
        'line2': '',
        'city': 'Gainesville',
        'state': 'FL',
        'zip': '32611',
        'country': 'US'}
