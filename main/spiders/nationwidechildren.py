from main.spiders.flintbox import FlintboxSpider


class NationwideChildrenHospitalSpider(FlintboxSpider):
    name = 'The Research Institute at Nationwide Children Hospital'
    start_urls = ['https://nationwidechildrens.flintbox.com/']
    address = {
        'line1': '700 Children Dr',
        'line2': '',
        'city': 'Columbus',
        'state': 'OH',
        'zip': '43205',
        'country': 'USA'}
