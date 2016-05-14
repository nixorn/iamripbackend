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


class MessageRoute(Resource):
    
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
            return {'id': m.id}, 201
        except:
            session.rollback()
            return {}, 400


class GetMessage(Resource):
    
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
                

api.add_resource(Register, '/register')
api.add_resource(IsFree, '/isfree')
api.add_resource(Me, '/me')
api.add_resource(Login, '/login')
api.add_resource(MessageRoute, '/message')
api.add_resource(GetMessage, '/message/<int:message_id>')


if __name__ == '__main__':
    app.run(debug=True)

