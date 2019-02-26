from main.spiders.unc import UncSpider


class ArizonaSpider(UncSpider):
    name = 'University of Arizona'
    start_urls = ['http://inventions.arizona.edu/technologies']
    address = {
        'line1': 'University of Arizona',
        'line2': '',
        'city': 'Tucson',
        'state': 'AZ',
        'zip': '85721',
        'country': 'US'}
