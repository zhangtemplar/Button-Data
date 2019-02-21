from main.spiders.flintbox import FlintboxSpider


class PurdueSpider(FlintboxSpider):
    name = 'Purdue Research Foundation'
    start_urls = ['https://prf.flintbox.com/']
    address = {
        'line1': '403 W Wood St',
        'line2': '',
        'city': 'West Lafayette',
        'state': 'IN',
        'zip': '47907',
        'country': 'US'}
