# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityHealthNetworkSpider(FlintboxSpider):
    name = 'University Health Network'
    start_urls = ['https://uhn.flintbox.com/']
    address = {
        'line1': 'R. Fraser Elliott Building, 1st Floor',
        'line2': '190 Elizabeth St.',
        'city': 'Toronto',
        'state': 'ON',
        'zip': '',
        'country': 'Canada'}