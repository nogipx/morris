from core.handlers.ChatHandler import ChatHandler
from database.DatabaseORM import Member
from database.DBProxy import DBProxy
from vk_communicate.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.group_manager.Group import Group


class VKManage:

    def __init__(self, token=None, login=None, password=None):
        self.storage = DBProxy(Member)
        self.session = BaseCommunicateVK.create_session(token, login, password)
        self.group = Group(self.session, self.storage).setup().update_members()
        self.chat = ChatHandler(self.group)

    def start(self):
        self.chat.run()

if __name__ == '__main__':
    VKManage(token="15798f19159f126d2fed5d3d35b8117661c969559694a739812b1ea929c2462fe1cda5dfa5e596d89e9aa").start()