# -*- coding: utf-8 -*-
import json
import os
import random
import time
from multiprocessing import Pool

from requests import get

from base.util import create_logger
from proxy.data5u import PROXY_THREAD
from proxy.pool import POOL


def find_list(log, work_directory: str, base_url: str, total_page: int) -> list:
    if os.path.exists(os.path.join(work_directory, 'links.json')):
        results = json.load(open(os.path.join(work_directory, 'links.json'), 'r'))
    else:
        results = []
        for page in range(1, total_page + 1):
            log.info('process page {}'.format(page))
            response = get(base_url.format(page))
            time.sleep(random.random())
            if 200 <= response.status_code < 300:
                data = response.json()
                results.extend(data['results'])
        with open(os.path.join(work_directory, 'links.json'), 'w') as fo:
            json.dump(results, fo)
    return results


def parse_page(log, work_directory: str, with_proxy: bool, slug: str):
    print('process {}'.format(slug))
    while True:
        try:
            if with_proxy:
                proxies = POOL.get()
                response = get(slug, proxies={'http': proxies, 'https': proxies})
            else:
                response = get(slug)
            if 200 <= response.status_code < 300:
                data = response.json()
                with open(os.path.join(work_directory, '{}.json'.format(slug.split('/')[-1])), 'w') as fo:
                    json.dump(data, fo)
                break
        except Exception as e:
            print(e)


def get_data(name: str, list_url: str, page_url: str, total_page: int, with_proxy: bool=False):
    log = create_logger(name)
    # each proxy need 5 seconds to start, there will be 16 proxies required to start
    time.sleep(5)
    work_directory = os.path.expanduser('~/Downloads/{}'.format(name))
    if not os.path.exists(work_directory):
        os.mkdir(work_directory)

    results = find_list(log, work_directory, list_url, total_page)
    slugs = []
    for r in results:
        if os.path.exists(os.path.join(work_directory, '{}.json'.format(
                r['opportunities'][0]['fileNumberSlug']))):
            log.debug('already processed {}'.format(r['opportunities'][0]['fileNumberSlug']))
            continue
        slugs.append(page_url.format(r['opportunities'][0]['fileNumberSlug']))
    if with_proxy:
        PROXY_THREAD.start()
    with Pool(16) as pool:
        pool.starmap(parse_page, [(None, work_directory, with_proxy, slug) for slug in slugs])
    if with_proxy:
        PROXY_THREAD.close()
