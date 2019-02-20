# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from bson import ObjectId

from schema.base import *


class Authentication(EmbeddedDocument):
    wechat = StringField(default='')
    linkedin = URLField(default='')
    pwd = StringField(default='')
    mac = StringField(default='')

    @staticmethod
    def default():
        return {'wechat': '', 'linkedin': '', 'pwd': '', 'mac': ''}


class Authorization(EmbeddedDocument):
    name = StringField(min_length=1, required=True)
    exp = DateTimeField(required=True)


class WorkExperience(EmbeddedDocument):
    title = StringField(default='')
    company = StringField(default='')

    @staticmethod
    def default():
        return {'title': '', 'company': ''}


class Education(EmbeddedDocument):
    degree = StringField(default='')
    major = StringField(default='')
    school = StringField(default='')

    @staticmethod
    def default():
        return {
            'degree': '',
            'major': '',
            'school': '',
        }


class Experience(EmbeddedDocument):
    real = StringField(default='')
    resume = URLField(default='')
    exp = EmbeddedDocumentField(WorkExperience, default=WorkExperience.default())
    edu = EmbeddedDocumentField(Education, default=Education.default())


class Entrepreneur(EmbeddedDocument):
    bp = StringField(default='')
    demand = EmbeddedDocumentField(Funding)
    fin = StringField(default='')
    market = StringField(default='')
    tech = StringField(default='')
    grant = StringField(default='')


class Investor(EmbeddedDocument):
    stage = IntField(min_value=0, max_value=13, default=11)
    amount = EmbeddedDocumentField(Currency, default=Currency.default())
    volume = EmbeddedDocumentField(Currency, default=Currency.default())


class Price(EmbeddedDocument):
    cost = EmbeddedDocumentField(Currency, default=Currency.default())
    eow = EmbeddedDocumentField(Currency, default=Currency.default())
    market = EmbeddedDocumentField(Currency, default=Currency.default())

    @staticmethod
    def default():
        return {
            'cost': Currency.default(),
            'eow': Currency.default(),
            'market': Currency.default(),
        }


class Asset(EmbeddedDocument):
    price = EmbeddedDocumentField(Price, default=Price.default())
    market = StringField(default='')
    tech = StringField(default='')
    lic = ListField(StringField(min_length=1), default='')
    stat = IntField(min_value=0, max_value=3, default=0)
    type = IntField(min_value=0, max_value=7, default=0)


class Group(EmbeddedDocument):
    parentId = ReferenceField('entity', default=ObjectId('000000000000000000000000'))
    memberId = ListField(ReferenceField('entity'), default=[])
    managerId = ListField(ReferenceField('entity'), default=[])


class Fund(EmbeddedDocument):
    currency = StringField(min_length=3, max_length=3, default='USD')
    type = IntField(min_value=0, max_value=16383, default=0)
    delegate = StringField(default='')
    stat = IntField(min_value=0, max_value=3, default=0)


class Portfolio(EmbeddedDocument):
    ids = ListField(ReferenceField('entity'), default=[])
    public = BooleanField(default=False)


class Lesson(EmbeddedDocument):
    name = StringField(min_length=1, required=True)
    url = URLField(required=True)
    public = BooleanField(default=False)


class Entity(Document):
    # required field
    name = StringField(min_length=1, required=True)
    addr = EmbeddedDocumentField(Address, required=True)
    contact = EmbeddedDocumentField(Contact, required=True)
    logo = URLField(default='')
    abs = StringField(min_length=1, required=True)
    type = IntField(min_value=0, required=True)
    tag = ListField(StringField(min_length=1), required=True)
    into = StringField(required=True)
    srcId = ReferenceField("self", default=ObjectId('000000000000000000000000'))
    pref = ListField(StringField(min_length=1), required=True)
    ref = StringField(default='', required=True)
    # read only field
    _deleted = BooleanField(default=False)
    _updated = DateTimeField(default=datetime.now())
    _created = DateTimeField(default=datetime.now())
    _auth = EmbeddedDocumentField(Authentication, default=Authentication.default())
    _perm = ListField(Authorization, required=False, default=[])
    # mark this class as base
    meta = {'allow_inheritance': True}


class ExpertEntity(Entity):
    type = 1
    exp = EmbeddedDocumentField(Experience)


class EntrepreneurEntity(Entity):
    type = 2
    exp = EmbeddedDocumentField(Experience)


class InvestorEntity(Entity):
    type = 4
    inv = EmbeddedDocumentField(Investor)


class AssetEntity(Entity):
    type = 8
    asset = EmbeddedDocumentField(Asset)


class GroupEntity(Entity):
    type = 32
    group = EmbeddedDocumentField(Group)


class FundEntity(Entity):
    type = 64
    fund = EmbeddedDocumentField(Fund)


class PortfolioEntity(Entity):
    type = 128
    portfolio = EmbeddedDocumentField(Portfolio)


class ClassEntity(Entity):
    type = 256
    lesson = EmbeddedDocumentListField(Lesson, default=[])
