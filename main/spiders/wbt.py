# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class WBTSpider(FlintboxSpider):
    name = 'WBT Innovation Marketplace'
    start_urls = ['https://wbt.flintbox.com/']
    address = {
        'line1': '13905 Quail Pointe Drive',
        'line2': 'Suite A',
        'city': 'Oklahoma City',
        'state': 'OK',
        'zip': '',
        'country': '73134'}