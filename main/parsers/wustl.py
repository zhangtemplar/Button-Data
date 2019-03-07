# -*- coding: utf-8 -*-

from main.parsers.angular import get_data

if __name__ == '__main__':
    get_data(
        'Washington University in St. Louis',
        'https://wustl.resoluteinnovation.com/api/searchResults?c=Home&qs=&fs=&p={}&docType=pub-opportunities&sort=relevance&precision=100',
        'https://wustl.resoluteinnovation.com/api/pub-opportunity/{}',
        18,
        False)
