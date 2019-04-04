# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from typing import List


class UnionFind(object):

    def __init__(self):
        self.data = {}

    def find(self, key):
        """
        Finds the set where key belongs to.

        :param key: any object can be used as a dictionary key
        :return: the key to the set
        """
        if key not in self.data:
            self.data[key] = key
            return key
        elif key == self.data[key]:
            return key
        else:
            # reduce the depth of the set
            result = self.find(self.data[key])
            self.data[key] = result
            return result

    def union(self, left, right):
        """
        Unions the sets which contains the keys. If the two keys belong to the same set, nothing will happen. If any
        :param left: any object can be used as a dictionary key
        :param right: any object can be used as a dictionary key
        :return: the key to the merged set
        """
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.data[right] = left
        return left

    def elements_in_set(self, key) -> List:
        """
        Returns all the element in the same set of key.

        :param key: any object can be used as a dictionary key
        :return: list of objects in the same set as key
        """
        root = self.find(key)
        return [r for r in self.data if self.find(r) == root]

    def all_elements(self) -> dict:
        """
        Returns all the elements in dictionary, where key is the one element (root) of the set, the value is all the
        elements in the same set as the key.

        :return: a dictionary
        """
        result = {}
        for d in self.data:
            k = self.find(d)
            if k not in result:
                result[k] = []
            result[k].append(d)
        return result
