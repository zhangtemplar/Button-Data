# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityVictoriaSpider(FlintboxSpider):
    name = 'The West Coast Licensing Partnership'
    start_urls = ['https://wcl.flintbox.com/']
    address = {
        'line1': '',
        'line2': '',
        'city': 'Unknown',
        'state': '',
        'zip': '',
        'country': 'UK'}