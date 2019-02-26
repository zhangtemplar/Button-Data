from main.spiders.flintbox import FlintboxSpider


class PaeteqSpider(FlintboxSpider):
    name = 'Parteq Innovations'
    start_urls = ['https://parteq.flintbox.com/']
    address = {
        'line1': '945 Princess Street',
        'line2': '',
        'city': 'Kingston',
        'state': 'ON',
        'zip': '',
        'country': 'Canada'}
