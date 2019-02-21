from main.spiders.flintbox import FlintboxSpider


class NorthwesternSpider(FlintboxSpider):
    name = 'Northwestern University'
    start_urls = ['http://northwestern.flintbox.com']
    address = {
        'line1': '633 Clark St',
        'line2': '',
        'city': 'Evanston',
        'state': 'IL',
        'zip': '60208',
        'country': 'US'}
