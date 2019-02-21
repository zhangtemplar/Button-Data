from main.spiders.flintbox import FlintboxSpider


class NorthernArizonaUniversitySpider(FlintboxSpider):
    name = 'OnSETT'
    start_urls = ['https://onsett.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'USA'}
