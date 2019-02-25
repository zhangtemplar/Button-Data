from main.spiders.nouvant import NouvantSpider


class NusSpider(NouvantSpider):
    name = 'National University of Singapore'
    start_urls = ['http://technology.nus.edu.sg/technologies']
    address = {
        'line1': '21 Heng Mui Keng Terrace',
        'line2': 'Level 5',
        'city': 'Singapore',
        'state': 'Singapore',
        'zip': 'S119613',
        'country': 'Singapore'}
