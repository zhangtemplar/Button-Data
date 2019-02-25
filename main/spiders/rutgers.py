from main.spiders.unc import UncSpider


class RutgersSpider(UncSpider):
    name = 'Rutgers, The State University of New Jersey'
    start_urls = ['http://license.rutgers.edu/technologies']
    address = {
        'line1': '33 Knightsbridge Road East',
        'line2': '2nd Floor',
        'city': 'Piscataway',
        'state': 'NJ',
        'zip': '08854',
        'country': 'US'}

    def statistics(self, response):
        return {'start': 0, 'end': 0, 'total': 0}
