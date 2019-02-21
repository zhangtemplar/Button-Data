from main.spiders.flintbox import FlintboxSpider


class LouisvilleSpider(FlintboxSpider):
    name = 'University of Louisville'
    start_urls = ['https://louisville.flintbox.com/']
    address = {
        'line1': '2301 S 3rd St',
        'line2': '',
        'city': 'Louisville',
        'state': 'KY',
        'zip': '40292',
        'country': 'US'}
