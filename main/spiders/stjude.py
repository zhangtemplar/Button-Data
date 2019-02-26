from main.spiders.flintbox import FlintboxSpider


class StJudeChildrenResearchHospitalSpider(FlintboxSpider):
    name = "St. Jude Children's Research Hospital"
    start_urls = ['https://stjude.flintbox.com/']
    address = {
        'line1': '262 Danny Thomas Place',
        'line2': '',
        'city': 'Memphis',
        'state': 'TN',
        'zip': '38105',
        'country': 'US'}
