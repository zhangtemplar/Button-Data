from main.spiders.university_california import UniversityCaliforniaSpider


class UclaSpider(UniversityCaliforniaSpider):
    name = 'University of California Los Angles'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=la&RunSearch=True']
    address = {
        'line1': '10889 Wilshire Blvd.',
        'line2': 'Suite 920',
        'city': 'Los Angeles',
        'state': 'CA',
        'zip': '90095',
        'country': 'US'}
