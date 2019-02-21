from main.spiders.flintbox import FlintboxSpider


class UniversityofIowaSpider(FlintboxSpider):
    name = 'University of Iowa'
    start_urls = ['https://uiowa.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Iowa City',
        'state': 'IA',
        'zip': '52242',
        'country': 'US'}
