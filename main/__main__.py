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


def process_nouvant_parallel():
    from main.spiders import nouvant
    from main.spiders.nouvant import NouvantSpider
    import os
    for module in os.listdir(os.path.dirname(nouvant.__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__('main.spiders.' + module[:-3], locals(), globals())
    del module
    crawlers = NouvantSpider.__subclasses__()
    print('Find crawlers: {}'.format([c.__name__ for c in crawlers]))
    process = CrawlerProcess(settings=get_project_settings())
    for c in crawlers:
        process.crawl(c)
    process.start()
    PROXY_THREAD.close()


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


def process_uc_sequentially():
    from main.spiders import university_california
    from main.spiders.university_california import UniversityCaliforniaSpider
    import os
    for module in os.listdir(os.path.dirname(university_california.__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__('main.spiders.' + module[:-3], locals(), globals())
    del module
    crawlers = UniversityCaliforniaSpider.__subclasses__()
    print('Find crawlers: {}'.format([c.__name__ for c in crawlers]))
    process = CrawlerProcess(settings=get_project_settings())
    start_sequentially(process, crawlers)
    process.start()
    PROXY_THREAD.close()


def start_sequentially(process: CrawlerProcess, crawlers: list):
    print('start crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0])
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_sequentially(process, crawlers[1:]))


if __name__ == '__main__':
    # process_flint_parallel()
    # process_uc_sequentially()
    process_nouvant_parallel()
    # from main.spiders.minnesota import MinnesotaSpider
    # process = CrawlerProcess(settings=get_project_settings())
    # process.crawl(MinnesotaSpider)
    # process.start()
    # PROXY_THREAD.close()

