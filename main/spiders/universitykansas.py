from main.spiders.flintbox import FlintboxSpider


class UniversityKansasSpider(FlintboxSpider):
    name = 'University of Kansas'
    start_urls = ['https://kuctc.flintbox.com/']
    address = {
        'line1': '1450 Jayhawk Blvd',
        'line2': '',
        'city': 'Lawrence',
        'state': 'KS',
        'zip': '66045',
        'country': 'USA'}
