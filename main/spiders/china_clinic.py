# -*- coding: utf-8 -*-
from base.buttonspider import ButtonSpider
import scrapy
import logging
import os
import json
import uuid
import random
from proxy.pool import POOL
import time


class ChinaClinicButtonSpider(ButtonSpider):
    name = 'china_clinic'
    allowed_domains = ['chictr.org.cn']
    work_directory = os.path.expanduser('~/Downloads/clinic')

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
                errback=self.handle_failure)
            time.sleep(random.random())

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

