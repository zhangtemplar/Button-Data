from main.spiders.flintbox import FlintboxSpider


class ChildrenHospitalLosAngelesSpider(FlintboxSpider):
    name = 'Children Hospital Los Angeles'
    start_urls = ['https://chla.flintbox.com/']
    address = {
        'line1': '4650 Sunset Blvd',
        'line2': '',
        'city': 'Los Angeles',
        'state': 'CA',
        'zip': '90027',
        'country': 'USA'}
