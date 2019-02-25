from main.spiders.flintbox import FlintboxSpider


class FlintboxAllSpider(FlintboxSpider):
    name = 'Cornell University'
    start_urls = ['https://cornell.flintbox.com/']
    address = {
        'line1': '616 Thurston Ave.',
        'line2': '',
        'city': 'Ithaca',
        'state': 'NY',
        'zip': '14853',
        'country': 'US'}
