from flask import Flask, Blueprint, request
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
            return {'token': u.token}, 201
        except:
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


api.add_resource(Home, '/')
api.add_resource(Register, '/register')
api.add_resource(IsFree, '/isfree')

if __name__ == '__main__':
    app.run(debug=True)

