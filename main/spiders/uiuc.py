from main.spiders.flintbox import FlintboxSpider


class UiucSpider(FlintboxSpider):
    name = 'University of Illinois at Urbana-Champaign'
    start_urls = ['https://illinois.flintbox.com/']
    address = {
        'line1': '202 Coble Hall',
        'line2': '801 South Wright Street',
        'city': 'Champaign',
        'state': 'IL',
        'zip': '61820',
        'country': 'USA'}
