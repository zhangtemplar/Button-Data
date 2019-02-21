from main.spiders.flintbox import FlintboxSpider


class C4Spider(FlintboxSpider):
    name = 'C4 Consortium'
    start_urls = ['https://c4.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'UK'}
