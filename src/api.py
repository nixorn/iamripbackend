import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from flask import Flask, Blueprint, request, make_response
from flask_restful import Resource, Api
from sqlalchemy import or_

from .models import *
from .engine import session
from .lib import *


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

    
class Register(Resource):
    def post(self):
        data = request.get_json()
        u = User(**data)
        try:
            session.add(u)
            session.commit()
            resp = make_response(json.dumps({}))
            resp.set_cookie('token', u.token)
            resp.status = '201'
            return resp
        except :
            session.rollback()
            return {}, 400


class IsFree(Resource):

    def post(self):
        data = request.get_json()
        users = session.query(User.email, User.username)\
                   .filter(or_(
                       User.username==data.get('username'),
                       User.email==data.get('email')
                   )).all()
        if not users:
            return {}, 200
        
        emails = [u.email for u in users]
        usernames = [u.username for u in users]

        fields = []
        if data.get('username') in usernames:
            fields.append('username')
        if data.get('email') in emails:
            fields.append('email')

        return {'fields': fields}, 409

class Me(Resource):

    def patch(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}
        users = session.query(User).filter(User.token==token).all()
        if not users:
            return {'message': 'unknown user'}
        try:    
            u = users[0]
            u.modify(**request.get_json())
            session.add(u)
            session.commit()
            return {}, 200
        except Exception as e:
            session.rollback()
            return {'message': str(e)}, 400
    
    def get(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}
        users = session.query(User).filter(User.token==token).all()
        if not users:
            return {'message': 'unknown user'}, 400
        else:
            u = users[0]
            return {'username': u.username,
                    'email': u.email,
                    'firstname': u.firstname,
                    'lastname': u.lastname}, 200


class Login(Resource):
    def get(self):
        data = request.get_json()
        try:
            u = session.query(User)\
                       .filter(User.username==data['username'], 
                               User.password==data['password']).one()
            resp = make_response(json.dumps({}))
            resp.set_cookie('token', u.token)
            resp.status = '200'
            return resp
        except:
            return {'message': 'Invalid login or password'}, 400


class MessagePoster(Resource):
    
    def post(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        users = session.query(User).filter(User.token==token).all()
        if not users:
            return {'message': 'unknown user'}, 400
        u = users[0]
        
        msg_dict = request.get_json()
        msg_dict.update(
            {'user_id': u.id}
        )
        
        duration = int(request.get_json()['duration'])
        
        m = Message(**msg_dict)
        session.add(m)
        session.commit()
        t = Timer(duration=duration,
                  created_at=str(datetime.now()),
                  next_checkdate=(datetime.now()+relativedelta(minutes=duration)),
                  message_id=m.id)
        session.add(t)
        session.commit()
        return {'id': m.id}, 201
        try:
            m = Message(**msg_dict)
            session.add(m)
            session.commit()
            t = Timer(duration=duration,
                      created_at=datetime.now(),
                      next_checkdate=datetime.now+relativedelta(minutes=duration),
                      message_id=m.id)
            session.add(t)
            session.commit()
            return {'id': m.id, 'id': m.uuid}, 201
        except:
            session.rollback()
            return {}, 400


class MessageManage(Resource):
    
    def get(self, message_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        message_id = int(message_id)

        m = session.query(Message).filter(Message.id==message_id).all()
        if not m:
            return {'message': 'no such message'}, 400
        m = m[0]
        
        owner = session.query(User).filter(User.token==token, User.id==m.user_id).all()
        if not owner:
            return {'message': 'this message is not yours'}, 400

        t = session.query(Timer).filter(Timer.message_id==m.id).all()
        if not t:
            return {'message': 'this message have no timer. something wrong'}, 400
        t = t[0]

        return {
            'text': m.text,
            'is_private': m.is_private,
            'is_processed': m.is_processed,
            'duration': t.duration}, 200

    def patch(self, message_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        message_id = int(message_id)

        m = session.query(Message).filter(Message.id==message_id).all()
        if not m:
            return {'message': 'no such message'}, 400
        m = m[0]
        
        owner = session.query(User).filter(User.token==token, User.id==m.user_id).all()
        if not owner:
            return {'message': 'this message is not yours'}, 400

        t = session.query(Timer).filter(Timer.message_id==m.id).all()
        if not t:
            return {'message': 'this message have no timer. something wrong'}, 400
        t = t[0]
        
        rq = request.get_json()

        duration = rq.get('duration')
        if duration:
            duration = int(duration)
            t.next_checkdate = str(t.next_checkdate + relativedelta(minutes=duration-t.duration))
            t.duration = duration
        
        text = rq.get('text')
        if text:
            m.text = text

        m.is_private = rq.get('is_private')
        try:
            session.add(m)
            session.add(t)
            session.commit()
        except:
            session.rollback()
            return {'message':'something wrong'}
        
        return {
            'text': m.text,
            'is_private': m.is_private,
            'is_processed': m.is_processed,
            'duration': t.duration}, 200

    def delete(self, message_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        message_id = int(message_id)

        m = session.query(Message).filter(Message.id==message_id).all()
        if not m:
            return {'message': 'no such message'}, 400
        m = m[0]
        
        owner = session.query(User).filter(User.token==token, User.id==m.user_id).all()
        if not owner:
            return {'message': 'this message is not yours'}, 400
        
        t = session.query(Timer).filter(Timer.message_id==m.id).all()
        if t:
            t = t[0]
            session.delete(t)

        d = session.query(Destination).filter(Destination.message_id==m.id).all()
        if d:
            d = d[0]
            session.delete(d)

        session.delete(m)
        try:
            session.commit()
            return {}, 200
        except:
            session.rollback()
            return {'message': 'something wrong'}, 400
                
class Messages(Resource):
    def get(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400

        owner = session.query(User).filter(User.token==token).all()
        if not owner:
            return {'message': 'unknown token'}, 400
        owner = owner[0]
        
        messages = session.query(Message.id, 
                                 Message.text,
                                 Message.is_private,
                                 Message.is_processed,
                                 Timer.duration)\
                          .filter(Message.user_id==owner.id,
                                  Timer.message_id==Message.id)\
                          .all()
        return {'messages':[
            {'id': m.id,
             'text': m.text,
             'is_private': m.is_private,
             'is_processed': m.is_processed,
             'duration': m.duration} for m in messages]}, 200


class Sources(Resource):
    def get(self):
        return {
            'sourcetypes': [
                {'id': s.id, 
                 'name': s.name} for s in session.query(Source).all()
            ]}, 200


class SourceRecordPoster(Resource):
    def post(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400

        owner = session.query(User).filter(User.token==token).all()
        if not owner:
            return {'message': 'unknown token'}, 400
        owner = owner[0]
        
        rec_dict = request.get_json()
        source = rec_dict['source_id']
        record_exists = session.query(SourceRecord)\
                               .filter(SourceRecord.user_id==owner.id,
                                       SourceRecord.source_id==source)\
                               .all()
        if record_exists:
            return {'message': 'such record already exists'}
        
        
        rec_dict.update({'user_id': owner.id})
        
        rec = SourceRecord(**rec_dict)
        try:
            session.add(rec)
            session.commit()
            return {}, 200
        except:
            session.rollback()
            return {'message': 'something wrong'}, 400
            

class SourceRecordManage(Resource):

    def get(self, sr_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400

        s = session.query(SourceRecord).filter(SourceRecord.id==sr_id).all()
        if not m:
            return {'message': 'no such source record'}, 400
        s = s[0]
        
        owner = session.query(User).filter(User.token==token, User.id==s.user_id).all()
        if not owner:
            return {'message': 'this source_record is not yours'}, 400

        return {
            'id': s.id,
            'source_id': s.source_id,
            'url': s.source_url}, 200

    def patch(self, sr_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        
        s = session.query(SourceRecord).filter(Message.id==sr_id).all()
        if not s:
            return {'message': 'no such message'}, 400
        s = s[0]
        
        owner = session.query(User).filter(User.token==token, User.id==s.user_id).all()
        if not owner:
            return {'message': 'this source record is not yours'}, 400

        rq = request.get_json()

        url = rq.get('url')
        if text:
            s.url = url
        try:
            session.add(s)
            session.commit()
        except:
            session.rollback()
            return {'message':'something wrong'}
        
        return {
            'url': s.url}, 200

    def delete(self, sr_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        
        s = session.query(SessionRecord).filter(SessionRecord.id==sr_id).all()
        if not s:
            return {'message': 'no such source record'}, 400
        s = s[0]
        
        owner = session.query(User).filter(User.token==token, User.id==s.user_id).all()
        if not owner:
            return {'message': 'this source record is not yours'}, 400
        
        session.delete(s)
        try:
            session.commit()
            return {}, 200
        except:
            session.rollback()
            return {'message': 'something wrong'}, 400


class SourceRecords(Resource):
    def get(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400

        owner = session.query(User).filter(User.token==token).all()

        if not owner:
            return {'message': 'unknown token'}, 400
        owner = owner[0]
        
        source_records = session.query(SourceRecord)\
                                .filter(owner.id==SourceRecord.user_id)\
                                .all()

        return {'source_records':[
            {'id': s.id,
             'source_id': s.source_id,
             'url': s.url} for s in source_records]}, 200


class Destinations(Resource):

    def get(self, message_id):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        
        res = session.query(Destination).filter(Destination.message_id==message_id,
                                                Message.id==message_id,
                                                Message.user_id==User.id,
                                                User.token==token)\
                                        .all()
        return {'destinations':[
            {'id': d.id,
             'email': d.email} for d in res]}

class DestinationPoster(Resource):

    def post(self):
        token = request.cookies.get('token')
        if not token:
            return {'message': 'log in please'}, 400
        
        owner = session.query(User).filter(User.token==token).all()
        if not owner:
            return {'message': 'unknown token'}, 400
        owner = owner[0]
        
        d = request.get_json()
        message_uuid =  d['message_uuid']
        email = d['mymail@gmail.com']
        m = session.query(Message).filter(Message.uuid==message_uuid).all()
        if not m:
            return {'message':'no message with such uuid'}, 400
        m = m[0]
        
        dest = Destination(message_id=m.id, email=email)
        try:
            session.add(dest)
            session.commit()
            return {}, 201
        except:
            session.rollback()
            return {'message': 'something wrong'}, 400

    
api.add_resource(Register, '/register')
api.add_resource(IsFree, '/isfree')
api.add_resource(Me, '/me')
api.add_resource(Login, '/login')
api.add_resource(MessagePoster, '/message')
api.add_resource(Destinations, '/message/<int:message_id>/destinations')
api.add_resource(MessageManage, '/message/<int:message_id>')
api.add_resource(Messages, '/me/messages')
api.add_resource(Sources, '/sources')
api.add_resource(SourceRecordPoster, '/source_record')
api.add_resource(SourceRecordManage, '/source_record/<int:sr_id>')
api.add_resource(SourceRecords, '/me/source_records')
api.add_resource(DestinationPoster, '/destination')


if __name__ == '__main__':
    app.run(debug=True)

