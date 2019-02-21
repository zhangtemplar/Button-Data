# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityMontanaSpider(FlintboxSpider):
    name = 'The University of Montana'
    start_urls = ['https://umt.flintbox.com/']
    address = {
        'line1': '32 Campus Dr',
        'line2': '',
        'city': 'Missoula',
        'state': 'MT',
        'zip': '59812',
        'country': 'US'}