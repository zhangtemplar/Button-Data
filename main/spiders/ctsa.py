from main.spiders.flintbox import FlintboxSpider


class ClinicalTranslationalScienceAwardsConsortiumSpider(FlintboxSpider):
    name = 'Clinical and Translational Science Awards Consortium'
    start_urls = ['https://ctsa.flintbox.com/']
    address = {
        'line1': '6701 Democracy Boulevard',
        'line2': '',
        'city': 'Bethesda',
        'state': 'MD',
        'zip': '20892',
        'country': 'USA'}
