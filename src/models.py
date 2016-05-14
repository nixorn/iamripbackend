from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey

from .engine import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    token = Column(String(32), unique=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    password = Column(String(32), nullable=False)

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.email = kwargs['email']
        self.token = kwargs.get('token')
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.password = kwargs['password']

    def __repr__(self):
        return '<User %r>' % self.username
    
    def modify(self, **kwargs):
        for field in kwargs.items():
            setattr(self, field[0], field[1])

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    user_id  = Column(Integer, ForeignKey('user.id'), nullable=False)
    content = Column(Text, nullable=False)
    uuid = Column(String(64), unique=True, nullable=False)
    is_processed = Column(Boolean)
    is_private = Column(Boolean)

    def __init__(self, **kwargs):
        self.user_id = kwargs['user_id']
        self.content = kwargs['content']
        self.uuid  = kwargs['uuid']
        self.is_processed = kwargs.get('is_processed')
        self.is_private  = kwargs['is_private']

    def __repr__(self):
        return '<Message %r>' % self.id


class Destination(Base):
    __tablename__ = 'destination'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)
    address = Column(String(200), nullable=False)

    def __init__(self, **kwargs):
        self.message_id = kwargs['message_id']
        self.address = kwargs['address']

    def __repr__(self):
        return '<Destination %r>' % self.address

		
class SourceRecord(Base):
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


class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def __repr__(self):
        return '<Source %r>' % self.name


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False) # minutes
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)
    next_checkdate = Column(DateTime)
    last_checkdate = Column(DateTime)

    def __init__(self, **kwargs):
        self.created_at = parse(kwargs['created_at'])
        self.duration = kwargs['created_at']
        self.message_id = kwargs['message_id']
        try:
            next_checkdate = parse(kwargs.get('next_checkdate'))
        except:
            next_checkdate = None
        try:
            last_checkdate = parse(kwargs.get('last_checkdate'))
        except:
            last_checkdate = None
        self.next_checkdate = next_checkdate
        self.last_checkdate = last_checkdate


    def __repr__(self):
        return '<Timer>' 
