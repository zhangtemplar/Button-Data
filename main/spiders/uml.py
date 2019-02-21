# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityMassachusettsLowellSpider(FlintboxSpider):
    name = 'University of Massachusetts Lowell'
    start_urls = ['https://uml.flintbox.com/']
    address = {
        'line1': '220 Pawtucket St',
        'line2': '',
        'city': 'Lowell',
        'state': 'MA',
        'zip': '01854',
        'country': 'US'}