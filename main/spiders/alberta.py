from main.spiders.flintbox import FlintboxSpider


class AlbertaAssociationSpider(FlintboxSpider):
    name = 'Alberta Association of Colleges & Technical Institutes'
    start_urls = ['https://aacti.flintbox.com/']
    address = {
        'line1': '210 Kingsway Professional Centre',
        'line2': '10611 Kingsway Avenue',
        'city': 'Edmonton',
        'state': 'Alberta',
        'zip': '',
        'country': 'Canada'}
