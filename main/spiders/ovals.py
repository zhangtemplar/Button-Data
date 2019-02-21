from main.spiders.flintbox import FlintboxSpider


class OhioValleyAffiliatesLifeSciencesSpider(FlintboxSpider):
    name = 'Ohio Valley Affiliates for Life Sciences'
    start_urls = ['https://ovals.flintbox.com/']
    address = {
        'line1': '1 Campus View Drive',
        'line2': '',
        'city': 'Vienna',
        'state': 'WV',
        'zip': '26105',
        'country': 'USA'}
