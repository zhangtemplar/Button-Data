from main.spiders.flintbox import FlintboxSpider


class CmuSpider(FlintboxSpider):
    name = 'Lawson Health Research Institute'
    start_urls = ['https://lhri.flintbox.com/']
    address = {
        'line1': '750 Base Line Road East',
        'line2': 'Suite 300',
        'city': 'London',
        'state': 'Ontario',
        'zip': 'N6C2R5',
        'country': 'Canada'}
