from main.spiders.flintbox import FlintboxSpider


class UniversityofArkansasSpider(FlintboxSpider):
    name = 'University of Arkansas at Little Rock'
    start_urls = ['https://ualr.flintbox.com/']
    address = {
        'line1': '2801 S University Ave',
        'line2': '',
        'city': 'Little Rock',
        'state': 'AR',
        'zip': '72204',
        'country': 'US'}
