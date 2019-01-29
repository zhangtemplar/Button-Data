# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""

from scrapy.crawler import CrawlerProcess

from main.spiders.pedata_exit import PedataExitSpider
from main.spiders.pedata_invest import PedataInvestSpider
from main.spiders.pedata_ipo import PedataIpoSpider
from main.spiders.pedata_ma import PedataMaSpider


def crawl_pedata():
    process = CrawlerProcess(settings={'LOG_LEVEL': 'INFO'})
    process.crawl(PedataMaSpider)
    process.crawl(PedataExitSpider)
    process.crawl(PedataIpoSpider)
    process.crawl(PedataInvestSpider)
    process.start()

if __name__ == '__main__':
    crawl_pedata()
