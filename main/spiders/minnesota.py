from main.spiders.texastech import TexasTechSpider


class MinnesotaSpider(TexasTechSpider):
    name = 'University of Minnesota'
    start_urls = ['http://license.umn.edu/technologies']
    address = {
        'line1': '200 Oak St. SE',
        'line2': 'Suite 228',
        'city': 'Minneapolis',
        'state': 'MN',
        'zip': '55455',
        'country': 'US'}
