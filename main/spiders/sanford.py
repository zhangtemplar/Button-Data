from main.spiders.flintbox import FlintboxSpider


class NorthernArizonaUniversitySpider(FlintboxSpider):
    name = 'Sanford Burnham Prebys Medical Discovery Institute'
    start_urls = ['https://sanfordburnham.flintbox.com/']
    address = {
        'line1': '10901 N Torrey Pines Rd',
        'line2': '',
        'city': 'La Jolla',
        'state': 'CA',
        'zip': '92037',
        'country': 'USA'}
