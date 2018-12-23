# -*- coding: utf-8 -*-
import scrapy
import logging
import os
import json
import uuid
import random
from proxy.pool import POOL
from proxy.data5u import GetProxyThread
import time


class ChinaClinicSpider(scrapy.Spider):
    name = 'china_clinic'
    allowed_domains = ['chictr.org.cn']
    work_directory = os.path.expanduser('~/Downloads/clinic')

    def __init__(self):
        super(scrapy.Spider, self).__init__()
        self.thread = GetProxyThread()
        self.thread.start()
        # wait for 10 seconds to build the pool
        time.sleep(10)

    @staticmethod
    def close(spider, reason):
        spider.thread.close()

    def start_requests(self):
        urls = json.load(open(os.path.join(self.work_directory, 'links.json'), 'rb'))
        for url in urls:
            page = uuid.uuid5(uuid.NAMESPACE_URL, url.encode('utf-8')).hex
            filename = '%s.html' % page
            if os.path.exists(os.path.join(self.work_directory, filename)):
                self.log('{} already exists'.format(url))
                continue
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'proxy': POOL.get()},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                },
                errback=self.handle_failure)
            time.sleep(random.random())

    def handle_failure(self, failure):
        POOL.remove(failure.request.meta['proxy'])

    def parse(self, response):
        # find the document url
        link = response.xpath("//div[@class='ProjetInfo_title']/a/@href").extract_first()
        if link is None:
            self.log('{} fail to download'.format(response.url, link), level=logging.WARNING)
            # remove the invalid proxy
            POOL.remove(response.request.meta['proxy'])
            return
        page = uuid.uuid5(uuid.NAMESPACE_URL, response.url.encode('utf-8')).hex
        filename = '%s.html' % page
        with open(os.path.join(self.work_directory, filename), 'wb') as f:
            f.write(response.body)
        self.log('{} => {}'.format(response.url, link), level=logging.INFO)
        yield {
            'link': response.url,
            'xml': link,
        }

