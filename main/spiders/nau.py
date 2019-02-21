from main.spiders.flintbox import FlintboxSpider


class NorthernArizonaUniversitySpider(FlintboxSpider):
    name = 'Northern Arizona University'
    start_urls = ['https://nau.flintbox.com/']
    address = {
        'line1': '1200 S Beaver St',
        'line2': '',
        'city': 'Flagstaff',
        'state': 'AZ',
        'zip': '86001',
        'country': 'USA'}
