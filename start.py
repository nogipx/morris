from core.handlers.DialogHandler import DialogHandler
from core.observers.CommandObserver import CommandObserver
from vk_communicate.controller.Group import Group

from commands.main.BroadcastCommand import AdminBroadcastCommand, BroadcastCommand
from commands.system.HelpCommand import HelpCommand

if __name__ == "__main__":
    group = Group("b007bb38c92f28b20c0011ba6682ebd7e1b266a988f6668cf6df2f1091dfdf4d9832911c5e4da1e36c506")
    observer = CommandObserver()
    observer.add(AdminBroadcastCommand(), BroadcastCommand(), HelpCommand())
    observer.make_keyboard()
    handler = DialogHandler(group, observer)
    handler.listen()
