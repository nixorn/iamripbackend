from config import login, password, app_id
import vk

session = vk.AuthSession(app_id=app_id, user_login=login, user_password=password)
api = vk.API(session)



