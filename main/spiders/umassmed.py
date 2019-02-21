# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityMassachusettsMedicalSchoolSpider(FlintboxSpider):
    name = 'University of Massachusetts Medical School'
    start_urls = ['https://umassmed.flintbox.com/']
    address = {
        'line1': '55 N Lake Ave',
        'line2': '',
        'city': 'Worcester',
        'state': 'MA',
        'zip': '01655',
        'country': 'US'}