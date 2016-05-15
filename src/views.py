from flask import Blueprint, render_template, abort, send_from_directory, make_response, request, redirect, url_for
from jinja2 import TemplateNotFound

from .models import *
from .engine import session
from .lib import *

import random

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

@views_bp.route('/message/<uuid>')
def show_message(uuid):
    m = session.query(Message).filter(Message.uuid==uuid).all()
    m = m[0]
    logged_in = False
    if is_user_logged_it(request):
        logged_in = True
        user = get_user(request)
    return render_template('message.jade', logged_in=logged_in, is_profile=False, message=m, user=user)

@views_bp.route('/random')
def show_random_message():
    m = session.query(Message).all()
    m = random.choice(m)
    user_id = m.user_id
    logged_in = False
    if is_user_logged_it(request):
        logged_in = True
    user = session.query(User).filter(User.id==user_id).first()
    return render_template('message_random.jade', logged_in=logged_in, is_profile=False, message=m, user=user)

@views_bp.route('/help')
def help():
    logged_in = False
    if is_user_logged_it(request):
        logged_in = True
    return render_template('help.jade', logged_in=logged_in, is_profile=False, message=m, user=user)

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
                {'id': s.id, 
                 'name': s.name} for s in session.query(Source).all()
            ]
    # print(real)
    # sources = [
        # { "name": "vk", "title": "ВКонтакте", "link": "vk.com" },
        # { "name": "twitter", "title": "Twitter", "link": "twitter.com" },
        # { "name": "facebook", "title": "Raw hash", "link": "anyurl" }
    # ]
    return render_template('profile_sources.jade', logged_in=True, is_profile=True, page="sources", sources=sources, user=user)

@views_bp.route('/profile/messages')
def profile_messages():
    if is_user_logged_it(request):
        user = get_user(request)
    else:
        return "Please, login first"
    # messages = [
        # {
            # "id": 250,
            # "text": "Some text there some text there",
            # "is_private": True,
            # "is_processed": False,
            # "duration": 3457,
            # "uuid": "347rtg97fh932h4f"
        # },
        # {
            # "id": 110,
            # "text": "Some text there some text there",
            # "is_private": True,
            # "is_processed": True,
            # "duration": 3457,
            # "uuid": "347297297e932h4f"
        # },
        # {
            # "id": 80,
            # "text": "Some small text there",
            # "is_private": False,
            # "is_processed": False,
            # "duration": 359,
            # "uuid": "0283rh0238fh23"
        # }
    # ]
    owner = user
    messages = session.query(Message.id, 
                            Message.text,
                            Message.uuid,
                            Message.is_private,
                            Message.is_processed,
                            Timer.duration)\
                        .filter(Message.user_id==owner.id,
                            Timer.message_id==Message.id)\
                        .all()
    real_messages = [
            {
                'id': m.id,
                'uuid': m.uuid,
                'text': m.text,
                'is_private': m.is_private,
                'is_processed': m.is_processed,
                'duration': m.duration} for m in messages ]


    for message in real_messages:
        message["hours"] = message["duration"] // 60
        message["minutes"] = message["duration"] % 60
    print(real_messages)
    return render_template('profile_messages.jade', logged_in=True, is_profile=True, page="messages", messages=real_messages, user=user)


@views_bp.route('/registration')
def registration():
    return render_template('registration.jade')
