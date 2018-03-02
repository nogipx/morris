from modules.commands.interface.IObserver import IObserver
import re

class CommandObserver(IObserver):

    __instance__ = None

    def execute(self, user_id, message, *args, **kwargs):
        result = None
        message = message.split()
        for command in self._commands:
            if not result:
                result = command.handle(user_id, message, *args, **kwargs)
        return result
