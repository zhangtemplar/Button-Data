from main.spiders.flintbox import FlintboxSpider


class CrossroadSpider(FlintboxSpider):
    name = 'The Crossroad for BioTransfer'
    start_urls = ['https://biotransfer.flintbox.com/']
    address = {
        'line1': '6100 Royalmount Avenue',
        'line2': '',
        'city': 'Montréal',
        'state': 'Quebec',
        'zip': '',
        'country': 'Canada'}
