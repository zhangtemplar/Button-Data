from main.spiders.flintbox import FlintboxSpider


class SalkSpider(FlintboxSpider):
    name = 'The Salk Institute'
    start_urls = ['https://salkinnovations.flintbox.com/']
    address = {
        'line1': '10010 N Torrey Pines Rd',
        'line2': '',
        'city': 'La Jolla',
        'state': 'CA',
        'zip': '92037',
        'country': 'US'}
