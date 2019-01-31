# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from main.spiders.cfda import CfdaSpider


def crawl_pedata():
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(CfdaSpider)
    process.start()

if __name__ == '__main__':
    crawl_pedata()
