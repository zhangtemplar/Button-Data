from main.spiders.nouvant import NouvantSpider


class MinnesotaSpider(NouvantSpider):
    name = 'Mayo Clinic'
    start_urls = ['http://technologies.ventures.mayoclinic.org/technologies']
    address = {
        'line1': '200 First St. SW',
        'line2': '',
        'city': 'Rochester',
        'state': 'MN',
        'zip': '55905',
        'country': 'US'}
