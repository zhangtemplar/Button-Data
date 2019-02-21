from main.spiders.flintbox import FlintboxSpider


class KansasStateUniversitySpider(FlintboxSpider):
    name = 'Kansas State University Research Foundation'
    start_urls = ['https://kstate.flintbox.com/']
    address = {
        'line1': '110 Anderson Hall',
        'line2': '919 Mid-Campus Drive North',
        'city': 'Manhattan',
        'state': 'KS',
        'zip': '66506',
        'country': 'USA'}
