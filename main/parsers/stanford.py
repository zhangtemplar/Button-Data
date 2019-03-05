# -*- coding: utf-8 -*-

from main.parsers.angular import get_data

if __name__ == '__main__':
    get_data(
        'Stanford',
        'http://techfinder.stanford.edu/api/searchResults?qs=&fs=&p={}&docType=pub-opportunities&sort=relevance&precision=100',
        'http://techfinder.stanford.edu/api/pub-opportunity/{}',
        74,
        False)
