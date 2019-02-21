from main.spiders.flintbox import FlintboxSpider


class ScrippsSpider(FlintboxSpider):
    name = 'The Scripps Research Institute'
    start_urls = ['https://scripps.flintbox.com/']
    address = {
        'line1': '10550 North Torrey Pines Road',
        'line2': '',
        'city': 'La Jolla',
        'state': 'CA',
        'zip': '92037',
        'country': 'USA'}
