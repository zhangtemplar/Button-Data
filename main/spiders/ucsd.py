from main.spiders.university_california import UniversityCaliforniaSpider


class UcsdSpider(UniversityCaliforniaSpider):
    name = 'University of California San Diego'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=SD&RunSearch=True']
    address = {
        'line1': '9500 Gilman Drive',
        'line2': 'MC 0910',
        'city': 'La Jolla',
        'state': 'CA',
        'zip': '92093',
        'country': 'US'}
