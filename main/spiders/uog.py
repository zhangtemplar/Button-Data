# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityGuelphSpider(FlintboxSpider):
    name = 'University of Guelph - Research Innovation Office'
    start_urls = ['https://uog.flintbox.com/']
    address = {
        'line1': '50 Stone Rd E',
        'line2': '',
        'city': 'Guelph',
        'state': 'ON',
        'zip': '',
        'country': 'Canada'}