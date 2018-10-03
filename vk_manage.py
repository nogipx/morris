from commands.BroadcastCommand import BroadcastCommand, AdminBroadcastCommand
from commands.SkippedLectionsCommand import SkippedLectionsCommand
from commands.TopicTimetableCommand import TopicTimetableCommand

from core.handlers.ChatHandler import ChatHandler
from core.observers.CommandObserver import CommandObserver
from database import DatabaseORM
from database.DatabaseORM import Member
from database.DBProxy import DBProxy
from vk_communicate.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.BotAccount import BotAccount
from vk_communicate.group_manager.Group import Group


class VKManage:

    def __init__(self, token=None, login=None, password=None):
        self.storage = DBProxy(DatabaseORM)
        self.session = BaseCommunicateVK.create_session(token, login, password)
        self.group = Group(self.session, self.storage).setup().update_members()
        self.chat = ChatHandler(self.group, CommandObserver.get_observer())
        self.bot = BotAccount.get_account().auth()

    def start(self):
        self.chat.run()

    def set_account(self):
        pass

    def get_command(self, command_name):
        return {
            "расписание": TopicTimetableCommand().setup_account(self.bot.api),
            "рассылка участникам": BroadcastCommand(),
            "рассылка админам": AdminBroadcastCommand(),
            "учет прогулов": SkippedLectionsCommand()
        }.get(command_name)

    def connect_command(self, command_name):
        command = self.get_command(str(command_name).lower())
        if command:
            self.chat.command_observer.add(command)
        return self

    def connect_commands(self, command_names):
        for i in command_names.split(','): self.connect_command(i.strip())
        return self

if __name__ == '__main__':
    VKManage(token="")\
        .connect_commands("рассылка участникам, рассылка админам, расписание, учет прогулов")\
        .start()