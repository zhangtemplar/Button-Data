from main.spiders.flintbox import FlintboxSpider


class FuentekSpider(FlintboxSpider):
    name = 'Fuentek LLC'
    start_urls = ['https://fuentek.flintbox.com/']
    address = {
        'line1': '10030 Green Level Ch Rd',
        'line2': 'Suite 802-117',
        'city': 'Cary',
        'state': 'NC',
        'zip': '27519',
        'country': 'USA'}
