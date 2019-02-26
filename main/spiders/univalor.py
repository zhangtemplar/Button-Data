from main.spiders.flintbox import FlintboxSpider


class UnivalorSpider(FlintboxSpider):
    name = 'Univalor'
    start_urls = ['https://univalor.flintbox.com/']
    address = {
        'line1': '3 Place Ville Marie',
        'line2': '',
        'city': 'Montreal',
        'state': 'QC',
        'zip': '',
        'country': 'Canada'}
