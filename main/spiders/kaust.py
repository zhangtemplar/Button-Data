from main.spiders.flintbox import FlintboxSpider


class KaustSpider(FlintboxSpider):
    name = 'Carnegie Mellon University'
    start_urls = ['https://kaust.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Thuwal',
        'state': '',
        'zip': '23955',
        'country': 'Saudi Arabia'}
