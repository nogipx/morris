from commands.BroadcastCommand import BroadcastCommand, AdminBroadcastCommand
from commands.TopicTimetableCommand import TopicTimetableCommand

from core.handlers.ChatHandler import ChatHandler
from core.observers.CommandObserver import CommandObserver
from database.DatabaseORM import Member
from database.DBProxy import DBProxy
from vk_communicate.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.group_manager.Group import Group


class VKManage:

    def __init__(self, token=None, login=None, password=None):
        self.storage = DBProxy(Member)
        self.session = BaseCommunicateVK.create_session(token, login, password)
        self.group = Group(self.session, self.storage).setup().update_members()
        self.chat = ChatHandler(self.group, CommandObserver.get_observer(CommandObserver))

    def start(self):
        self.chat.run()

    def set_account(self):
        pass

    def get_command(self, command_name):
        return {
            "расписание": TopicTimetableCommand,
            "рассылка участникам": BroadcastCommand,
            "рассылка админам": AdminBroadcastCommand,
            # "учет прогулов": SkipedLessonsCommand
        }.get(command_name)

    def connect_command(self, command_name):
        command = self.get_command(str(command_name).lower())
        if command:
            self.chat.command_observer.add(command())
        return self

if __name__ == '__main__':
    VKManage(token="15798f19159f126d2fed5d3d35b8117661c969559694a739812b1ea929c2462fe1cda5dfa5e596d89e9aa")\
        .connect_command("рассылка участникам")\
        .connect_command("рассылка админам")\
        .start()