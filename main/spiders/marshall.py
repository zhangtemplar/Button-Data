from main.spiders.flintbox import FlintboxSpider


class MarshallSpider(FlintboxSpider):
    name = 'Marshall University'
    start_urls = ['https://marshall.flintbox.com/']
    address = {
        'line1': '1 John Marshall Dr',
        'line2': '',
        'city': 'Huntington',
        'state': 'WV',
        'zip': '25755',
        'country': 'US'}
