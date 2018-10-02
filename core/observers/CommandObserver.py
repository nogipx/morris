from commands.interface.IObserver import IObserver


class CommandObserver(IObserver):

    __instance__ = None

    def execute(self, user_id, message, *args, **kwargs):
        result = None
        message = message.split()
        for command in self._commands:
            if len(message) >= 1 and message[0] in command.triggers:
                result = command.handle(user_id, message, *args, **kwargs)
        return result
