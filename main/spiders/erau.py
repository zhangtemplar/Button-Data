from main.spiders.flintbox import FlintboxSpider


class EmbryRiddleAeronauticalUniversitySpider(FlintboxSpider):
    name = 'Embry-Riddle Aeronautical University'
    start_urls = ['https://erau.flintbox.com/']
    address = {
        'line1': '600 South Clyde Morris Blvd',
        'line2': '',
        'city': 'Daytona Beach',
        'state': 'FL',
        'zip': '32114',
        'country': 'USA'}
