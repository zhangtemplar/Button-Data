# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityVictoriaSpider(FlintboxSpider):
    name = 'University of Victoria'
    start_urls = ['https://uvic.flintbox.com/']
    address = {
        'line1': '3800 Finnerty Rd',
        'line2': '',
        'city': 'Victoria',
        'state': 'BC',
        'zip': '',
        'country': 'Canada'}