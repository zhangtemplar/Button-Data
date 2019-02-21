from main.spiders.flintbox import FlintboxSpider


class McMasterSpider(FlintboxSpider):
    name = 'McMaster University'
    start_urls = ['https://mcmaster.flintbox.com/']
    address = {
        'line1': '1280 Main St W',
        'line2': '',
        'city': 'Hamilton',
        'state': 'ON',
        'zip': '',
        'country': 'Canada'}
