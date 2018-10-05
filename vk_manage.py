from commands.main.BroadcastCommand import BroadcastCommand, AdminBroadcastCommand
from commands.applied.SkippedLectionsCommand import SkippedLectionsCommand
from commands.applied.TopicTimetableCommand import TopicTimetableCommand
from commands.system.HelpCommand import HelpCommand

from core.handlers.ChatHandler import ChatHandler
from core.observers.CommandObserver import CommandObserver
from core.settings.ConfigParser import ConfigParser

from database import DatabaseORM
from database.DBProxy import DBProxy

from vk_communicate.controller.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.controller.BotAccount import BotAccount
from vk_communicate.controller.Group import Group

from settings import *


class VKManage:

    def __init__(self, token=None, login=None, password=None):
        self.session = BaseCommunicateVK.create_session(token, login, password)

        self.storage = DBProxy(DatabaseORM)
        self.group = Group(self.session, self.storage).setup().update_members()
        self.chat = ChatHandler(self.group, CommandObserver.get_observer())
        self.bot = BotAccount.get_account().auth(login, password)

    def start(self):
        self.chat.run()

    def set_account(self):
        pass

    def get_command(self, command_name):
        return {
            "рассылка участникам": BroadcastCommand(),
            "рассылка админам": AdminBroadcastCommand(),
            "помощь": HelpCommand(),
            "учет прогулов": SkippedLectionsCommand(),
            "расписание": TopicTimetableCommand().setup_account(self.bot.api),
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
    config = ConfigParser(project_path)

    VKManage(token=config['token'], login=config['login'], password=config['password'])\
        .connect_commands("помощь, рассылка участникам, рассылка админам, учет прогулов")\
        .start()