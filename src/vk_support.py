from config import token
import vk

session = vk.Session(access_token=token)
api = vk.API(session)
