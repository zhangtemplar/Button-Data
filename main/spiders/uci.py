from main.spiders.university_california import UniversityCaliforniaSpider


class UciSpider(UniversityCaliforniaSpider):
    name = 'University of California Irvine'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=ir&RunSearch=True']
    address = {
        'line1': '5141 California Avenue',
        'line2': 'Suite 200',
        'city': 'Irvine',
        'state': 'CA',
        'zip': '92697',
        'country': 'US'}
