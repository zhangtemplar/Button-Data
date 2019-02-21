from main.spiders.flintbox import FlintboxSpider


class IitSpider(FlintboxSpider):
    name = 'Illinois Institute of Technology'
    start_urls = ['https://iit.flintbox.com/']
    address = {
        'line1': '10 W 35th St',
        'line2': '',
        'city': 'Chicago',
        'state': 'IL',
        'zip': '60616',
        'country': 'USA'}
