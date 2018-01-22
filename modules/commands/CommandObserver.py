from modules.interfaces.IObserver import IObserver


class CommandObserver(IObserver):

    __instance__ = None

    def execute(self, user_id, cmd):
        result = ''
        for command in self._commands:
            if not result:
                result = command.handle(user_id, cmd)
        return result
