# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from datetime import datetime

from mongoengine import *


class Address(EmbeddedDocument):
    line1 = StringField(default='')
    line2 = StringField(default='')
    city = StringField(min_length=1, required=True)
    state = StringField(default='')
    country = StringField(min_length=1, required=True)
    zip = StringField(default='')


class Contact(EmbeddedDocument):
    phone = StringField(default='')
    email = EmailField(default='')
    website = URLField(default='')
    meet = URLField(default='')


class Currency(EmbeddedDocument):
    amount = FloatField(min_value=0, default='')
    unit = StringField(min_length=3, max_length=3, default='USD')

    @staticmethod
    def default():
        return {'amount': 0, 'unit': 'USD'}


class Funding(EmbeddedDocument):
    stage = IntField(min_value=0, max_value=13)
    amount = EmbeddedDocumentField(Currency, default=Currency.default())
    val = EmbeddedDocumentField(Currency, default=Currency.default())
    share = FloatField(min_value=0, max_value=1)
    due = DateTimeField(default=datetime.now())

    @staticmethod
    def default():
        return {
            'stage': 11,
            'amount': Currency.default(),
            'val': Currency.default(),
            'share': 0.0,
            'due': datetime.now(),
        }
