from main.spiders.flintbox import FlintboxSpider


class RiceSpider(FlintboxSpider):
    name = 'Rice University'
    start_urls = ['https://rice.flintbox.com/']
    address = {
        'line1': '1155 York Avenue',
        'line2': '',
        'city': 'New York',
        'state': 'NY',
        'zip': '10065',
        'country': 'US'}
