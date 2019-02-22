# -*- coding: utf-8 -*-
import json
import logging
import os
import time
import random
from requests import get

from base.buttonspider import ButtonSpider
from proxy.pool import POOL
from proxy.data5u import PROXY_THREAD
from multiprocessing import Pool
from base.util import create_logger


def find_list() -> list:
    if os.path.exists(os.path.join(work_directory, 'links.json')):
        results = json.load(open(os.path.join(work_directory, 'links.json'), 'r'))
    else:
        results = []
        for page in range(1, 75):
            log.info('process page {}'.format(page))
            response = get(
                'http://techfinder.stanford.edu/api/searchResults?qs=&fs=&p={}&docType=pub-opportunities&sort=relevance&precision=100'.format(
                    page))
            time.sleep(random.random())
            if 200 <= response.status_code < 300:
                data = response.json()
                results.extend(data['results'])
        with open(os.path.join(work_directory, 'links.json'), 'w') as fo:
            json.dump(results, fo)
    return results


def parse_page(slug: str):
    log.info('process {}'.format(slug))
    while True:
        try:
            proxies = POOL.get()
            response = get(
                'http://techfinder.stanford.edu/api/pub-opportunity/{}'.format(slug),
                proxies={'http': proxies, 'https': proxies})
            if 200 <= response.status_code < 300:
                data = response.json()
                with open(os.path.join(work_directory, '{}.json'.format(slug)), 'w') as fo:
                    json.dump(data, fo)
                break
        except Exception as e:
            log.error(e)

class StanfordSpider(ButtonSpider):
    allowed_domains = ['techfinder.stanford.edu']
    start_urls = ['http://techfinder.stanford.edu/technologies/S18-354_nanoparticle-hydrogels-for']
    address = {
        "country": "US",
        "line2": "",
        "city": "Stanford",
        "zip": "94305",
        "state": "CA",
        "line1": "450 Serra Mall"}


if __name__ == '__main__':
    name = 'Stanford'
    log = create_logger(name)
    PROXY_THREAD.start()
    # each proxy need 5 seconds to start, there will be 16 proxies required to start
    time.sleep(5)
    work_directory = os.path.expanduser('~/Downloads/{}'.format(name))
    if not os.path.exists(work_directory):
        os.mkdir(work_directory)

    results = find_list()
    slugs = []
    for r in results:
        if os.path.exists(os.path.join(work_directory, '{}.json'.format(
                r['opportunities'][0]['fileNumberSlug']))):
            log.debug('already processed {}'.format(r['opportunities'][0]['fileNumberSlug']))
            continue
        slugs.append(r['opportunities'][0]['fileNumberSlug'])
    with Pool(16) as pool:
        pool.map(parse_page, slugs)
    PROXY_THREAD.close()
