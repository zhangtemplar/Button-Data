from base.buttonspider import ButtonSpider


class NorthCarolinaStateUniversitySpider(ButtonSpider):
    name = 'North Carolina State University'
    start_urls = ['https://research.ncsu.edu/commercialization/available-technologies/']
    address = {
        'line1': '10 Watauga Club Drive',
        'line2': '',
        'city': 'Raleigh',
        'state': 'NC',
        'zip': '27695',
        'country': 'US'}
