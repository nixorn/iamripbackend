from datetime import datetime()
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import time

from .vk_support import api
from .engine import *
from .models import *

def process_message(msg):
    
    pass

while 1:
    current_timers = session.query(Timer)\
                            .filter(Timer.next_checkdate >= datetime.now() - relativedelta(minutes=5))\
                            .all()
    for timer in current_timers:
        msg = session.query(Message).filter(Message.id==timer.message_id).first()
        process_message(msg)
        

    time.sleep(240)
