import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, Blueprint, request, make_response
from flask_restful import Resource, Api
from sqlalchemy import or_

from .models import *
from .engine import session
from .lib import *


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class Home(Resource):
    def get(self):
        return {'foo': 'bar'}
    
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
            return {'message': 'log in please'}
        users = session.query(User).filter(User.token==token).all()
        if not users:
            return {'message': 'unknown user'}, 400
        u = users[0]
        
        msg_dict = request.get_json()
        msg_dict.update(
            {'user_id': u.id}
        )

        try:
            m = Message(**msg_dict)
            session.add(m)
            session.commit()
            return {'id': m.id}, 201
        except:
            session.rollback()
            return {}, 400



api.add_resource(Home, '/')
api.add_resource(Register, '/register')
api.add_resource(IsFree, '/isfree')
api.add_resource(Me, '/me')
api.add_resource(Login, '/login')
api.add_resource(MessageRoute, '/message')

if __name__ == '__main__':
    app.run(debug=True)

