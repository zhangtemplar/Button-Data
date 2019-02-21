# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityIllinoisChicagoSpider(FlintboxSpider):
    name = 'University of Illinois at Chicago'
    start_urls = ['https://uic.flintbox.com/']
    address = {
        'line1': '1200 W Harrison St',
        'line2': '',
        'city': 'Chicago',
        'state': 'IL',
        'zip': '60607',
        'country': 'US'}