# coding=utf-8
from main.spiders.flintbox import FlintboxSpider

__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


class UniversityTexasArlingtonSpider(FlintboxSpider):
    name = 'University of Texas at Arlington'
    start_urls = ['https://uta.flintbox.com/']
    address = {
        'line1': '701 W Nedderman Dr',
        'line2': '',
        'city': 'Arlington',
        'state': 'TX',
        'zip': '76019',
        'country': 'US'}