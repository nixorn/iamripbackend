from flask import Blueprint, render_template, abort, send_from_directory, make_response, request, redirect, url_for
from jinja2 import TemplateNotFound

from .models import *
from .engine import session
from .lib import *

views_bp = Blueprint('views_bp', __name__, template_folder='templates')

def is_user_logged_it(request):
    token = request.cookies.get('token')
    if token:
        user = session.query(User).filter(User.token==token).first()
        if user:
            return True
    return False

def get_user(request):
    token = request.cookies.get('token')
    if token:
        user = session.query(User).filter(User.token==token).first()
        if user:
            return user
    return False

@views_bp.route('/')
def index():
    logged_in = False
    if is_user_logged_it(request):
        logged_in = True
    return render_template('index.jade', logged_in=logged_in, is_profile=False)

@views_bp.route('/profile')
@views_bp.route('/profile/settings')
def profile_settings():
    if is_user_logged_it(request):
        user = get_user(request)
    else:
        return redirect(url_for('views_bp.index'))
    return render_template('profile_settings.jade', page="settings", logged_in=True, is_profile=True, user=user)

@views_bp.route('/profile/sources')
def profile_sources():
    if is_user_logged_it(request):
        user = get_user(request)
    else:
        return "Please, login first"
    sources = [
        { "name": "vk", "title": "ВКонтакте", "link": "vk.com" },
        { "name": "twitter", "title": "Twitter", "link": "twitter.com" },
        { "name": "hash", "title": "Raw hash", "link": "anyurl" }
    ]
    return render_template('profile_sources.jade', logged_in=True, is_profile=True, page="sources", sources=sources, user=user)

@views_bp.route('/registration')
def registration():
    return render_template('registration.jade')
