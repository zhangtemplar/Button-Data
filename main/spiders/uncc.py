# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityNorthCarolinaCharlotteSpider(FlintboxSpider):
    name = 'University of North Carolina Charlotte'
    start_urls = ['https://uncc.flintbox.com/']
    address = {
        'line1': '9201 University City Blvd',
        'line2': '',
        'city': 'Charlotte',
        'state': 'NC',
        'zip': '28223',
        'country': 'US'}