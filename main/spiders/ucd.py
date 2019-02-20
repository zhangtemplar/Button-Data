from main.spiders.university_california import UniversityCaliforniaSpider


class UcdSpider(UniversityCaliforniaSpider):
    name = 'University of California Davis'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=da&RunSearch=True']
    address = {
        'line1': '1850 Research Park Drive',
        'line2': 'Suite 100',
        'city': 'Davis',
        'state': 'CA',
        'zip': '95618',
        'country': 'US'}
