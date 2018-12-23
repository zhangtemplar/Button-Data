# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""

import requests
import time
import threading
from pool import POOL


class GetProxyThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, target=self.run)
        super(threading.Thread, self).__init__()
        self.delay_second = 5
        self.api_url = "http://api.ip.data5u.com/dynamic/get.html?order=7d8a85dd7a1f85cc74e8140fa3711848"
        self.token = ','
        self.running = threading.Event()
        self.running.set()

    def run(self):
        """
        The main function
        """
        while self.running.is_set():
            proxy = requests.get(self.api_url).content.decode().split(self.token)
            print('add new proxy {} to pool'.format(proxy))
            for p in proxy:
                POOL.add('http://' + p[:-1])
            time.sleep(self.delay_second)

    def close(self):
        """
        Closes the thread
        """
        self.running.clear()
