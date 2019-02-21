# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityKentuckySpider(FlintboxSpider):
    name = 'University of Kentucky'
    start_urls = ['https://uky.flintbox.com/']
    address = {
        'line1': '410 Administration Dr',
        'line2': '',
        'city': 'Lexington',
        'state': 'KY',
        'zip': '40506',
        'country': 'US'}