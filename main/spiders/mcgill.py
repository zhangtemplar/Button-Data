from main.spiders.flintbox import FlintboxSpider


class McGillSpider(FlintboxSpider):
    name = 'McGill University'
    start_urls = ['https://mcgill.flintbox.com/']
    address = {
        'line1': '845 Sherbrooke St W',
        'line2': '',
        'city': 'Montréal',
        'state': 'Quebec',
        'zip': '',
        'country': 'Canada'}
