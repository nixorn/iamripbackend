from flask import Flask, Blueprint, request 
from flask_restful import Resource, Api
from uuid import uuid4
from .models import *
from .engine import *
from .api import api_bp
from .views import views_bp


app = Flask(__name__, static_folder='static', static_url_path='')
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(views_bp)

if __name__ == '__main__':
    app.run(debug=True)

