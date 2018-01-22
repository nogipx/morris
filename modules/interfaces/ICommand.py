from abc import ABCMeta, abstractmethod


class ICommand(metaclass=ABCMeta):

    def __init__(self):
        self._triggers = []
        self._when_activate = []

    @abstractmethod
    def proceed(self, *args):
        pass

    def add_activate_time(self, *times):
        for time in times:
            self._when_activate.append(time)

    def handle(self, user_id, command):
        cmd = command.split()
        print(cmd)
        for key in cmd:
            if key in self._triggers:
                func = cmd[0]
                args = cmd[1:]
                return self.proceed(user_id, func, *args)