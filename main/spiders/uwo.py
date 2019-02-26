from main.spiders.flintbox import FlintboxSpider


class WORLDiscoveriesSpider(FlintboxSpider):
    name = 'WORLDiscoveries'
    start_urls = ['https://uwo.flintbox.com/']
    address = {
        'line1': '100 Collip Circle',
        'line2': 'Suite 105',
        'city': 'London',
        'state': 'Ontario',
        'zip': '',
        'country': 'Canada'}
