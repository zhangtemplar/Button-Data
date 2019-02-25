from main.spiders.texastech import TexasTechSpider


class DelawareNouvantSpider(TexasTechSpider):
    name = 'University of Delaware (Nouvant)'
    start_urls = ['http://innovation.oeip.udel.edu/technologies']
    address = {
        'line1': '1 Innovation Way',
        'line2': '',
        'city': 'Newark',
        'state': 'DE',
        'zip': '19716',
        'country': 'US'}
