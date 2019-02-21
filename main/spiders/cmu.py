from main.spiders.flintbox import FlintboxSpider


class CmuSpider(FlintboxSpider):
    name = 'Carnegie Mellon University'
    start_urls = ['https://cmu.flintbox.com/']
    address = {
        'line1': '5000 Forbes Avenue',
        'line2': '',
        'city': 'Pittsburgh',
        'state': 'PA',
        'zip': '15213',
        'country': 'US'}
