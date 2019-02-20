from main.spiders.university_california import UniversityCaliforniaSpider


class UcsfSpider(UniversityCaliforniaSpider):
    name = 'University of California San Francisco'
    start_urls = ['https://techtransfer.universityofcalifornia.edu/Default.aspx?campus=sf&RunSearch=True#']
    address = {
        'line1': '600 16th St',
        'line2': 'Genentech Hall, S-272',
        'city': 'San Francisco',
        'state': 'CA',
        'zip': '94158',
        'country': 'US'}
