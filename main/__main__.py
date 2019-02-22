# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from proxy.data5u import PROXY_THREAD
from main.spiders.ucb import UcbSpider
from main.spiders.ucd import UcdSpider
from main.spiders.uci import UciSpider
from main.spiders.ucla import UclaSpider
from main.spiders.ucsb import UcsbSpider
from main.spiders.ucsc import UcscSpider
from main.spiders.ucsd import UcsdSpider
from main.spiders.ucsf import UcsfSpider


def process_flint_parallel():
    from main.spiders import flintbox
    from main.spiders.flintbox import FlintboxSpider
    import os
    for module in os.listdir(os.path.dirname(flintbox.__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__('main.spiders.' + module[:-3], locals(), globals())
    del module
    crawlers = FlintboxSpider.__subclasses__()
    print('Find crawlers: {}'.format([c.__name__ for c in crawlers]))
    process = CrawlerProcess(settings=get_project_settings())
    for c in crawlers:
        process.crawl(c)
    process.start()
    PROXY_THREAD.close()


def start_next(process: CrawlerProcess, crawlers: list):
    print('start crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0])
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_next(process, crawlers[1:]))


def main():
    process = CrawlerProcess(settings=get_project_settings())
    crawlers = [UcbSpider, UcdSpider, UciSpider, UclaSpider, UcsbSpider, UcscSpider, UcsdSpider, UcsfSpider]
    start_next(process, crawlers)
    process.start()
    PROXY_THREAD.close()


if __name__ == '__main__':
    main()
