from config import token
import vk

sess = vk.Session(access_token=token)
api = vk.API(session)
