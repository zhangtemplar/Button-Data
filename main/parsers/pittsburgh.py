# -*- coding: utf-8 -*-
from main.parsers.angular import get_data


if __name__ == '__main__':
    name = 'University of Pittsburgh'
    get_data(
        'University of Pittsburgh',
        'http://licensing.innovation.pitt.edu/api/searchResults?qs=&fs=&p={}&docType=pub-opportunities&sort=relevance&precision=100',
        'http://licensing.innovation.pitt.edu/api/pub-opportunityFat/{}',
        28,
        False
    )
