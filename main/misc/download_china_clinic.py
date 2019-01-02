# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import logging
import os
import random
import threading
import time
import json
from bs4 import BeautifulSoup
from lxml import etree
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from proxy.pool import POOL
from proxy.data5u import PROXY_THREAD


class DownloadChinaClinic(threading.Thread):

    def __init__(self, links, work_directory):
        super().__init__()
        self.links = links
        self.work_directory = work_directory
        self.running = threading.Event()

    def get_webdriver(self):
        capacity = DesiredCapabilities().CHROME
        option = webdriver.ChromeOptions()
        option.add_experimental_option(
            "prefs",
            {
                # uncomment to allow image
                "profile.managed_default_content_settings.images": 2,
                # uncomment to allow stream
                "profile.managed_default_content_settings.media_stream": 2,
                "profile.default_content_settings.popups": 0,
                "download.default_directory": self.work_directory,
            })
        # we could create a new driver.
        option.add_argument("--proxy-server={}".format(POOL.pop()))
        # option.add_argument("--headless")
        driver = webdriver.Chrome(
            os.path.expanduser('~/chromedriver'),
            desired_capabilities=capacity,
            options=option)
        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {'behavior': 'allow', 'downloadPath': self.work_directory}}
        command_result = driver.execute("send_command", params)
        return driver

    def run(self):
        index = 0
        driver = self.get_webdriver()
        self.running.set()
        while index < len(self.links) and self.running.is_set():
            link = self.links[index]
            logging.info('process link {}'.format(link))
            try:
                driver.get(link)
                not_found = driver.find_elements_by_xpath('//*[@id="main-message"]/h1/span')
                if len(not_found) != 0:
                    raise AssertionError('Unable to open the page')
                index += 1
                time.sleep(5 * random.random())
            except Exception as e:
                logging.error(e)
                logging.warning('fail to download {}'.format(link))
                try:
                    driver.close()
                finally:
                    driver = self.get_webdriver()

    def close(self):
        self.running.clear()

def find_url():
    work_directory = os.path.expanduser('~/Downloads/clinic')
    links = []
    for file in os.listdir(work_directory):
        if not file.endswith('.html'):
            continue
        print('process file {}'.format(file))
        with open(os.path.join(work_directory, file), 'r') as fi:
            soup = BeautifulSoup(fi.read(), 'html.parser')
            link = soup.select_one('.ProjetInfo_title > a').get('href')
            print('find link {}'.format(link))
            links.append(link)
    with open(os.path.join(work_directory, 'links.json'), 'w') as fo:
        json.dump(links, fo)

def scanAndRename(work_directory):
    project_ids = []
    for file in os.listdir(work_directory):
        if not file.endswith('xml'):
            continue
        try:
            data = etree.parse(os.path.join(work_directory, file))
            url = data.xpath('/trials/Triall/main/url')[0].text
        except:
            logging.warning("{} cannot be parsed".format(file))
            os.remove(os.path.join(work_directory, file))
            continue
        project_id = url.split('=')[-1]
        os.rename(os.path.join(work_directory, file), os.path.join(work_directory, project_id + '.xml'))
        project_ids.append(project_id)
    return project_ids

def download_china_clinic():
    logging.basicConfig(level=logging.INFO)
    work_directory = os.path.expanduser('~/Downloads/clinic')
    project_ids = set(scanAndRename(work_directory))

    with open(os.path.join(work_directory, 'links.json'), 'r') as fi:
        links = json.load(fi)
    links = ['http://www.chictr.org.cn/' + l for l in links]
    links = [l for l in links if parse_qs(urlparse(l).query)['v'][0] not in project_ids]
    logging.info('{} links are found'.format(len(links)))
    number_threads = 1
    threads = []
    PROXY_THREAD.start()
    time.sleep(5)
    for t in range(number_threads):
        logging.info('create new thread {}'.format(t))
        thread = DownloadChinaClinic([links[i] for i in range(t, len(links), number_threads)], work_directory)
        thread.start()
        threads.append(thread)
        time.sleep(5)

    for t in threads:
        t.join()
    PROXY_THREAD.close()


if __name__ == '__main__':
    download_china_clinic()
