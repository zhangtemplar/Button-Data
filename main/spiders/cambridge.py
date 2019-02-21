from main.spiders.flintbox import FlintboxSpider


class CambridgeSpider(FlintboxSpider):
    name = 'University of Cambridge'
    start_urls = ['https://cambridge.flintbox.com/']
    address = {
        'line1': 'The Old Schools',
        'line2': 'Trinity Ln',
        'city': 'Cambridge',
        'state': '',
        'zip': '',
        'country': 'UK'}
