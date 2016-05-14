from flask import Flask, Blueprint, request 
from flask_restful import Resource, Api
from uuid import uuid4
from .models import *
from .engine import *
from .api import api_bp


app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')    

if __name__ == '__main__':
    app.run(debug=True)

