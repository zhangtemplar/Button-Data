from main.spiders.flintbox import FlintboxSpider


class FederalPartnersTechnologyTransferSpider(FlintboxSpider):
    name = 'Federal Partners in Technology Transfer'
    start_urls = ['https://fptt.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'USA'}
