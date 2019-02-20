# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from schema.base import *
from schema.entity import Entity


class Step(EmbeddedDocument):
    name = StringField(min_length=1)
    status = IntField(min_value=0, max_value=3)
    opId = ListField(ReferenceField(Entity), default=[])


class Task(EmbeddedDocument):
    addr = EmbeddedDocumentField(Address, required=True)
    step = EmbeddedDocumentListField(Step)



class Fee(EmbeddedDocument):
    pct = FloatField(min_value=0, max_value=1, default=0)
    eqt = FloatField(min_value=0, default=0)
    fee = EmbeddedDocumentField(Currency, default=Currency.default())


    @staticmethod
    def default():
        return {'pct': 0, 'eqt': 0, 'fee': Currency.default()}


class FaFee(EmbeddedDocument):
    src = EmbeddedDocumentField(Fee, default=Fee.default())
    pfm = EmbeddedDocumentField(Fee, default=Fee.default())
    op = EmbeddedDocumentListField(Fee, default=[])


    @staticmethod
    def default():
        return {'src': Fee.default(), 'pfm': Fee.default(), 'op': []}


class Fa(EmbeddedDocument):
    fee = EmbeddedDocumentField(FaFee, default=FaFee.default())


class QA(EmbeddedDocument):
    q = StringField(default='')
    a = StringField(default='')


    @staticmethod
    def default():
        return {'q': '', 'a': ''}


class Interview(EmbeddedDocument):
    addr = EmbeddedDocumentField(Address, required=True)
    qa = EmbeddedDocumentListField(QA, default=[])
    sum = StringField(default='')
    plan = StringField(default='')


class Deal(EmbeddedDocument):
    amount = EmbeddedDocumentField(Currency, default=Currency.default())
    share = FloatField(min_value=0)


    @staticmethod
    def default():
        return {'amount': Currency.default(), 'share': 0}


class Investment(EmbeddedDocument):
    demand = EmbeddedDocumentField(Funding, default=Funding.default())
    deal = EmbeddedDocumentListField(Deal, default=[])


class Operation(Document):
    srcId = ReferenceField(Entity, required=True)
    dstId = ReferenceField(Entity, required=True)
    opId = ListField(ReferenceField(Entity), default=[])
    name = StringField(min_length=1, required=True)
    abs = StringField(min_length=1, required=True)
    detail = StringField(default='')
    tag = ListField(StringField(min_length=1), default=[])
    start = DateTimeField(default=datetime.now())
    end = DateTimeField(default=datetime.now())
    type = IntField(min_value=0, max_value=3, default=0)
    prior = IntField(min_value=0, max_value=5, default=0)
    stat = IntField(min_value=0, max_value=3, default=0)
    ref = StringField(default='')
    _deleted = BooleanField(default=False)
    _created = DateTimeField(default=datetime.now())
    _updated = DateTimeField(default=datetime.now())

    meta = {'allow_inheritance': True}
    extra = EmbeddedDocumentField()


class TaskOperation(Operation):
    type = 0
    extra = EmbeddedDocumentField(Task)


class FaOperation(Operation):
    type = 1
    extra = EmbeddedDocumentField(Fa)


class InterviewOperation(Operation):
    type = 2
    extra = EmbeddedDocumentField(Interview)


class InvestmentOperation(Operation):
    type = 3
    extra = EmbeddedDocumentField(Investment)
