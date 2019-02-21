# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityBritishColumbiaSpider(FlintboxSpider):
    name = 'University of British Columbia'
    start_urls = ['https://ubc.flintbox.com/']
    address = {
        'line1': '2329 West Mall',
        'line2': '',
        'city': 'Vancouver ',
        'state': 'BC',
        'zip': '',
        'country': 'Canada'}