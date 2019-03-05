# -*- coding: utf-8 -*-

from main.parsers.angular import get_data

if __name__ == '__main__':
    get_data(
        'Columbia University',
        'http://innovation.columbia.edu/api/searchResults?qs=&fs=&p={}&docType=pub-opportunities&sort=relevance&precision=100',
        'http://innovation.columbia.edu/api/pub-opportunity/{}',
        76)
