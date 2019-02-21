# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class SpringboardSpider(FlintboxSpider):
    name = 'TECHSTORM'
    start_urls = ['https://techstorm.flintbox.com/']
    address = {
        'line1': '10 Anson Rd',
        'line2': 'Building 10-11 International Plaza',
        'city': 'Singapore',
        'state': '',
        'zip': '',
        'country': 'Singapore'}