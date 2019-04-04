# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import requests


def create_relationship():
    return {
        "url": "",
        "type": 0,
        "dstId": "",
        "name": "",
        "end": "Thu, 01 Jan 1970 00:00:00 GMT",
        "srcId": "",
        "stat": 0,
        "abs": "",
        "detail": "",
        "tag": [],
        "start": "Thu, 01 Jan 1970 00:00:00 GMT",
        "ref": ""
    }


def create_user():
    return {
        "type": 1,
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "ref": "",
        "abs": "",
        "name": "",
        "nick": "",
        "onepage": {
            'banner': '',
            'bg': '',
            'prod': '',
            'high': '',
            'team': '',
        },
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "exp": {
            'resume': "",
            'exp': {'title': '', 'company': ''},
            'edu': {'degree': '', 'major': '', 'school': ''},
        },
        "tag": []
    }


def create_company():
    return {
        "type": 2,
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "ref": "",
        "name": "",
        "abs": "",
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "nick": "",
        "onepage": {
            'banner': '',
            'bg': '',
            'prod': '',
            'high': '',
            'team': '',
        },
        "entr": {
            "bp": "",
            "demand": {
                "stage": 11,
                "amount": {"amount": 0, "unit": "USD"},
                "val": {"amount": 0, "unit": "USD"},
                "share": 0,
                "due": "Thu, 01 Jan 1970 00:00:00 GMT",
            },
            "fin": "",
            "market": "",
            "tech": "",
            "grant": "",
        },
        "tag": []
    }


def create_product():
    return {
        "type": 8,
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "ref": "",
        "name": "",
        "abs": "",
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "tag": [],
        "nick": "",
        "onepage": {
            'banner': '',
            'bg': '',
            'prod': '',
            'high': '',
            'team': '',
        },
        'asset': {
            'price': {
                'cost': {"amount": 0.0, 'unit': "USD"},
                'eow': {"amount": 0.0, 'unit': "USD"},
                'market': {"amount": 0.0, 'unit': "USD"},
            },
            'market': "",
            'tech': "",
            'lic': [],
            'stat': 0,
            'type': 0,
            'ind': []
        }
    }



def add_record(resource, data):
    try:
        return requests.post('http://172.17.0.7/' + resource, json=data).json()
    except Exception as e:
        print(e)
        return {'_status': 'Err'}
