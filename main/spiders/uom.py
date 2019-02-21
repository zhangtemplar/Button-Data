# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityManitobaSpider(FlintboxSpider):
    name = 'University of Manitoba'
    start_urls = ['https://uom.flintbox.com/']
    address = {
        'line1': '66 Chancellors Cir',
        'line2': '',
        'city': 'Winnipeg',
        'state': 'MB',
        'zip': '',
        'country': 'Canada'}