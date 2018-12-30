# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""

from time import time
import random
import logging


class ExpirationSet(object):
    """
    A set which associates the expiration time for each of its entry
    """
    def __init__(self, expiration_seconds, expiration_count=9223372036854775807):
        """
        Initializes the expiration pool with expiration time

        :param expiration_seconds: the number of seconds before the item becomes expired
        :param expiration_count: the number of times used before the item becomes invalid
        """
        self.data = {}
        self.expiration_seconds = expiration_seconds
        self.expiration_count = expiration_count
        self.seed = random.seed()

    def add(self, key, expiration_seconds=None, expiration_count=None):
        """
        Adds a new data to the pool

        :param key: new data
        :param expiration_seconds: if not provided, the class-wise expiration time will be used
        :param expiration_count: if not provided, the class-wise expiration count will be used
        """
        if expiration_seconds is None:
            expiration_seconds = self.expiration_seconds
        if expiration_count is None:
            expiration_count = self.expiration_count
        timestamp = time()
        self.data[key] = [expiration_seconds + time(), 0]
        # remove all the old keys
        keys = list(self.data.keys())
        for k in keys:
            # remove the expired or overused item
            if self.data[k][0] < timestamp or self.data[k][1] > expiration_count:
                logging.debug('remove invalid proxy {}:{}/{}'.format(k, self.data[k][0], self.data[k][1]))
                del self.data[k]

    def remove(self, key):
        if key in self.data:
            logging.debug('remove invalid proxy {}:{}/{}'.format(key, self.data[key][0], self.data[key][1]))
            del self.data[key]
        else:
            logging.warning('{} is not in pool'.format(key))

    def get(self):
        """
        Gets a data which is not yet expired

        :return: the data if available, otherwise None
        """
        if len(self.data.keys()) < 1:
            logging.warning('the pool is empty now')
            return None
        key = random.choice(list(self.data.keys()))
        # increase the count
        self.data[key][1] += 1
        return key

    def pop(self):
        """
        Pops a data from the pool.

        :return: the data if available, otherwise None
        """
        if len(self.data.keys()) < 1:
            logging.warning('the pool is empty now')
            return None
        key = random.choice(list(self.data.keys()))
        del self.data[key]
        return key


POOL = ExpirationSet(300)
