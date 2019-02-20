from main.spiders.university_california import UniversityCaliforniaSpider


class UcbSpider(UniversityCaliforniaSpider):
    name = 'University of California Berkeley'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?RunSearch=true&campus=BK']
    address = {
        'line1': '2150 Shattuck Avenue',
        'line2': 'Suite 510',
        'city': 'Berkeley',
        'state': 'CA',
        'zip': '94704',
        'country': 'US'}
