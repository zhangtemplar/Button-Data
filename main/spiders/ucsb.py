from main.spiders.university_california import UniversityCaliforniaSpider


class UcsbSpider(UniversityCaliforniaSpider):
    name = 'University of California Santa Barbara'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=sb&RunSearch=True']
    address = {
        'line1': '342 Lagoon Road',
        'line2': '',
        'city': 'Santa Barbara',
        'state': 'CA',
        'zip': '93106',
        'country': 'US'}
