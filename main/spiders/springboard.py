# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class SpringboardSpider(FlintboxSpider):
    name = 'Springboard'
    start_urls = ['https://springboard.flintbox.com/']
    address = {
        'line1': '22 Battery Street',
        'line2': 'Ste 320',
        'city': 'San Francisco',
        'state': 'CA',
        'zip': '94111',
        'country': 'USA'}