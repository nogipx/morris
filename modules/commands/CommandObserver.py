from modules.commands.intefaces.ICommandObserver import ICommandObserver
from BotAccount import AlreadyCreatedError


class CommandObserver(ICommandObserver):
    __instance__ = None

    def __init__(self):
        self._commands = []

    @staticmethod
    def get_command_observer():
        if CommandObserver.__instance__ is None:
            CommandObserver.__instance__ = CommandObserver()
        else:
            raise AlreadyCreatedError("CommandObserver has been already created")
        return CommandObserver.__instance__
    
    def add_commands(self, *args):
        for arg in args:
            self._commands.append(arg)

    def command(self, cmd):
        result = ''
        for command in self._commands:
            if not result:
                result = command.handle(cmd)
        return result
