from main.spiders.flintbox import FlintboxSpider


class LifeSciencesBritishColumbiaSpider(FlintboxSpider):
    name = 'LifeSciences British Columbia'
    start_urls = ['https://lifesciencesbc.flintbox.com/']
    address = {
        'line1': '1285 West Broadway',
        'line2': 'Suite 580',
        'city': 'Vancouver',
        'state': 'British Columbia',
        'zip': '',
        'country': 'Canada'}
