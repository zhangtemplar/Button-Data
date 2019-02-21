from main.spiders.flintbox import FlintboxSpider


class DalhousieSpider(FlintboxSpider):
    name = 'Dalhousie University'
    start_urls = ['https://dalhousie.flintbox.com/']
    address = {
        'line1': '6299 South St',
        'line2': '',
        'city': 'Halifax',
        'state': 'New Brunswick',
        'zip': '',
        'country': 'Canada'}
