# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from main.spiders.ucb import UcbSpider
from main.spiders.ucd import UcdSpider
from main.spiders.uci import UciSpider
from main.spiders.ucla import UclaSpider
from main.spiders.ucsb import UcsbSpider
from main.spiders.ucsc import UcscSpider
from main.spiders.ucsd import UcsdSpider
from main.spiders.ucsf import UcsfSpider


def main():
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(UcbSpider)
    process.crawl(UcdSpider)
    process.crawl(UciSpider)
    process.crawl(UclaSpider)
    process.crawl(UcsbSpider)
    process.crawl(UcscSpider)
    process.crawl(UcsdSpider)
    process.crawl(UcsfSpider)
    process.start()

if __name__ == '__main__':
    main()
