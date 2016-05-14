from flask import Flask, request
from flask_restful import Resource, Api
from .models import *
from .engine import *

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
    
    def post(self):
        data = request.get_json()
        return data

api.add_resource(HelloWorld, '/')



if __name__ == '__main__':
    app.run(debug=True)

