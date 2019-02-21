from main.spiders.flintbox import FlintboxSpider


class UniversityofTexasElPasoSpider(FlintboxSpider):
    name = 'The University of Texas at El Paso'
    start_urls = ['https://utep.flintbox.com/']
    address = {
        'line1': '500 W University Ave',
        'line2': '',
        'city': 'El Paso',
        'state': 'TX',
        'zip': '79968',
        'country': 'US'}
