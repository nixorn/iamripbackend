from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

views_bp = Blueprint('views_bp', __name__, template_folder='templates')
@views_bp.route('/registration')
def registration():
    try:
        return render_template('registration.jade')
    except TemplateNotFound:
        abort(404)
