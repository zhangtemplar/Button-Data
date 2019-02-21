from main.spiders.flintbox import FlintboxSpider


class BoyceThompsonInstituteSpider(FlintboxSpider):
    name = 'Boyce Thompson Institute'
    start_urls = ['https://bti.flintbox.com/']
    address = {
        'line1': '533 Tower Rd',
        'line2': '',
        'city': 'Ithaca',
        'state': 'NY',
        'zip': '14853',
        'country': 'USA'}
