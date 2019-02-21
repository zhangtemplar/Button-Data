from main.spiders.flintbox import FlintboxSpider


class CanadianVirtualCollegeConsortiumSpider(FlintboxSpider):
    name = 'Canadian Virtual College Consortium'
    start_urls = ['https://blaze.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'Canada'}
