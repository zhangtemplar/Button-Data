from main.spiders.flintbox import FlintboxSpider


class GeorgetownSpider(FlintboxSpider):
    name = 'Georgetown University'
    start_urls = ['https://georgetown.flintbox.com/']
    address = {
        'line1': '3700 O St NW',
        'line2': '',
        'city': 'Washington',
        'state': 'DC',
        'zip': '20057',
        'country': 'USA'}
