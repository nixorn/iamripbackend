import json
from flask import Flask, Blueprint, request, make_response
from flask_restful import Resource, Api
from sqlalchemy import or_
from uuid import uuid4
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
        u.token = uuid4().hex
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
        users = session.query(User).filter(User.token==token).all()
        if not users:
            return {'message': 'unknown user'}, 400
        else:
            u = users[0]
            return {'username': u.username,
                    'email': u.email,
                    'firstname': u.firstname,
                    'lastname': u.lastname}, 200
        
            

api.add_resource(Home, '/')
api.add_resource(Register, '/register')
api.add_resource(IsFree, '/isfree')
api.add_resource(Me, '/me')

if __name__ == '__main__':
    app.run(debug=True)

