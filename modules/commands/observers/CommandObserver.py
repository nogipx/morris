from modules.commands.interface.IObserver import IObserver


class CommandObserver(IObserver):

    __instance__ = None

    def execute(self, user_id, message, *args, **kwargs):
        result = None
        for command in self._commands:
            if result == 'IGNORE':
                return result
            if not result:
                result = command.handle(user_id, message, *args, **kwargs)
        return result
