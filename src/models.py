from uuid import uuid4
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .engine import Base


class ModelMixin(object):
    def modify(self, **kwargs):
        for field in kwargs.items():
            setattr(self, field[0], field[1])
    

class User(Base, ModelMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    token = Column(String(32), unique=True, nullable=False)
    firstname = Column(String(100))
    lastname = Column(String(100))
    password = Column(String(32), nullable=False)

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.email = kwargs['email']
        self.token = uuid4().hex
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.password = kwargs['password']

    def __repr__(self):
        return '<User %r>' % self.username
    

class Message(Base, ModelMixin):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    user_id  = Column(Integer, ForeignKey('user.id'), nullable=False)
    text = Column(Text, nullable=False)
    uuid = Column(String(64), unique=True, nullable=False)
    is_processed = Column(Boolean)
    is_private = Column(Boolean)

    def __init__(self, **kwargs):
        self.user_id = kwargs['user_id']
        self.text = kwargs['text']
        self.uuid  = uuid4().hex
        self.is_processed = kwargs.get('is_processed')
        self.is_private  = kwargs.get('is_private')

    def __repr__(self):
        return '<Message %r>' % self.id


class Destination(Base, ModelMixin):
    __tablename__ = 'destination'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)
    address = Column(String(200), nullable=False)

    def __init__(self, **kwargs):
        self.message_id = kwargs['message_id']
        self.address = kwargs['address']

    def __repr__(self):
        return '<Destination %r>' % self.address


class SourceRecord(Base, ModelMixin):
    __tablename__ = 'source_record'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('source.id'), nullable=False)
    url = Column(String(200), nullable=False)

    def __init__(self, **kwargs):
        self.user_id = kwargs['user_id']
        self.source_id = kwargs['source_id']
        self.url = kwargs['url']

    def __repr__(self):
        return '<SourceRecord %r>' % self.url


class Source(Base, ModelMixin):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def __repr__(self):
        return '<Source %r>' % self.name


class Timer(Base, ModelMixin):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False) # minutes
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)
    next_checkdate = Column(DateTime)
    last_checkdate = Column(DateTime)

    def __init__(self, **kwargs):
        self.created_at = str(datetime.now())
        self.duration = kwargs['duration']
        self.message_id = kwargs['message_id']
        self.next_checkdate = str(datetime.now() + relativedelta(minutes=int(self.duration)))
        self.last_checkdate = str(datetime.now())

    def __repr__(self):
        return '<Timer %s>'%self.id

