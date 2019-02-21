from main.spiders.flintbox import FlintboxSpider


class TamuSpider(FlintboxSpider):
    name = 'Texas A&M University'
    start_urls = ['https://tamus.flintbox.com/']
    address = {
        'line1': '400 Bizzell St',
        'line2': '',
        'city': 'College Station',
        'state': 'TX',
        'zip': '77843',
        'country': 'US'}
