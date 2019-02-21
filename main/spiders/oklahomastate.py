from main.spiders.flintbox import FlintboxSpider


class NorthernArizonaUniversitySpider(FlintboxSpider):
    name = 'Oklahoma State University'
    start_urls = ['https://okstate.flintbox.com/']
    address = {
        'line1': '120 Agriculture North',
        'line2': '',
        'city': 'Stillwater',
        'state': 'OK',
        'zip': '74078',
        'country': 'USA'}
