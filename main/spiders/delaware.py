from main.spiders.flintbox import FlintboxSpider


class DelawareSpider(FlintboxSpider):
    name = 'University of Delaware'
    start_urls = ['https://udel.flintbox.com/']
    address = {
        'line1': '1 Innovation Way',
        'line2': '',
        'city': 'Newark',
        'state': 'DE',
        'zip': '19716',
        'country': 'US'}
