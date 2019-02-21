from main.spiders.flintbox import FlintboxSpider


class LouisianaStateUniversitySpider(FlintboxSpider):
    name = 'Louisiana State University'
    start_urls = ['https://lsu.flintbox.com/']
    address = {
        'line1': '156 Thomas Boyd Hall',
        'line2': '',
        'city': 'Baton Rouge',
        'state': 'LA',
        'zip': '70803',
        'country': 'USA'}
