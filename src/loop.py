from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import time

from .vk_support import get_last_visit_vk
from .engine import *
from .models import *
    

def process_message(message_id):
    message = session.query(Message)\
                     .filter(Message.id==message_id).one()
    message.is_processed = True
    session.add(message)
    session.commit()



def process_timer(timer):
    user = session.query(User)\
                  .filter(User.id==Message.user_id,
                          Message.id==timer.message_id)\
                  .all()
    if not user:
        raise Exception('Timer have no user? WTF?')
    user = user[0]
    
    records = session.query(SourceRecord.url, Source.name)\
                     .filter(SourceRecord.user_id==user.id,
                             Source.id==SourceRecord.source_id)\
                     .all()
    
    parse_vk_id = lambda x: int(x.split('id')[-1])
    
    visits = []
    for record in records:
        if record.name == 'vk':
            last_visit = get_last_visit_vk(record)
            visits.append(visit)
    if not visits:
        return

    activity_marker = max(visits)
    
    if activity_marker + relativedelta(minutes=timer.duration) > timer.next_checkdate:
        timer.next_checkdate = activity_marker + relativedelta(minutes=timer.duration)
        timer.last_checkdate = datetime.now()
        try:
            session.add(timer)
            session.commit()
            return
        except:
            session.rollback()
            raise Exception('cant commit timer!')
    else:
        process_message(message_id)

def loop():
    while 1:
        current_timers = session.query(Timer)\
                                .filter(Timer.next_checkdate >= datetime.now() - relativedelta(minutes=5))\
                                .all()
        
        for t in current_timers:
            process_timer(t)

        time.sleep(240)
