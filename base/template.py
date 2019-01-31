# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""


def create_relationship():
    return {
        "url": "",
        "type": 0,
        "dstId": "",
        "name": "",
        "end": None,
        "srcId": "",
        "status": 0,
        "abs": "",
        "detail": "",
        "tag": [],
        "start": None,
        "ref": ""
    }


def create_user():
    return {
        "type": 1,
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "ref": "",
        "abs": "",
        "name": "",
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "exp": {
            'real': "",
            'resume': "",
            'exp': {'title': '', 'company': ''},
            'edu': {'degree': '', 'major': '', 'school': ''},
        },
        "tag": []
    }


def create_company():
    return {
        "type": 1,
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "ref": "",
        "name": "",
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "group": {
            'parentId': "",
            'mgrId': [],
            'memberId': [],
        },
        "entr": {
            "bp": "",
            "demand": {
                "stage": 11,
                "amount": {"amount": 0, "unit": "USD"},
                "val": {"amount": 0, "unit": "USD"},
                "share": 0,
                "due": "",
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
        "srcId": "000000000000000000000000",
        "addr": {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""},
        "contact": {"website": "", "meet": "", "email": "", "phone": ""},
        "intro": "",
        "tag": [],
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
        }
    }
