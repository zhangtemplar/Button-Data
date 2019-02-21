# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityTexasSanAntonioSpider(FlintboxSpider):
    name = 'University of Texas at San Antonio'
    start_urls = ['https://utsa.flintbox.com/']
    address = {
        'line1': '1 UTSA Circle',
        'line2': '',
        'city': 'San Antonio',
        'state': 'TX',
        'zip': '78249',
        'country': 'US'}