from main.spiders.nouvant import NouvantSpider


class MichiganSpider(NouvantSpider):
    name = 'University of Michigan'
    start_urls = ['http://inventions.umich.edu/technologies']
    address = {
        'line1': '500 S State St',
        'line2': '',
        'city': 'Ann Arbor',
        'state': 'MI',
        'zip': '48109',
        'country': 'US'}
