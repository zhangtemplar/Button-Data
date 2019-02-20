from main.spiders.university_california import UniversityCaliforniaSpider


class UcscSpider(UniversityCaliforniaSpider):
    name = 'University of California Santa Cruz'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=sc&RunSearch=True']
    address = {
        'line1': 'Kerr 413 / IATC',
        'line2': '',
        'city': 'Santa Cruz',
        'state': 'CA',
        'zip': '95064',
        'country': 'US'}
