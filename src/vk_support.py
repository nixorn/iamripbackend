from .config import login, password, app_id
from datetime import datetime
import vk

session = vk.AuthSession(app_id=app_id, user_login=login, user_password=password)
vk_api = vk.API(session)

def get_last_visit_vk(id):
    try:
        last_visit = vk_api.users.get(user_ids=id, fields=['last_seen'])
        last_visit = last_visit[0]['last_seen']['time']
        last_visit = datetime.fromtimestamp(last_visit)
        return last_visit
    except Exception as e:
        print(e)
        return None



