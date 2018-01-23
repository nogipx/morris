from modules.interfaces.IObserver import IObserver


class CommandObserver(IObserver):

    __instance__ = None

    def execute(self, user_id, message):
        result = ''
        for command in self._commands:
            if not result:
                result = command.handle(user_id, message)
        return result
