from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

views_bp = Blueprint('views_bp', __name__, template_folder='templates')

@views_bp.route('/')
def index():
    return render_template('index.jade')

@views_bp.route('/registration')
def registration():
    return render_template('registration.jade')
