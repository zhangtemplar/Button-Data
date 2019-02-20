# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
from schema.base import *
from schema.entity import Entity


class Relationship(Document):
    srcId = ReferenceField(Entity, required=True)
    dstId = ReferenceField(Entity, required=True)
    name = StringField(min_length=1, required=True)
    abs = StringField(min_length=1, required=True)
    detail = StringField(default='')
    tag = ListField(StringField(min_length=1), default=[])
    start = DateTimeField(default=datetime.now())
    end = DateTimeField(default=datetime.now())
    type = IntField(min_value=0, max_value=11, default=0)
    url = URLField(default='')
    stat = IntField(min_value=0, max_value=3, default=0)
    ref = StringField(default='')
    _deleted = BooleanField(default=False)
    _created = DateTimeField(default=datetime.now())
    _updated = DateTimeField(default=datetime.now())
