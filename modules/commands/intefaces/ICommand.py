from abc import ABCMeta, abstractmethod


class ICommand(metaclass=ABCMeta):

    def __init__(self):
        self._triggers = []

    @abstractmethod
    def proceed(self, args):
        pass

    def handle(self, command):
        cmd = command.split()
        for key in cmd:
            if key in self._triggers:
                args = cmd[1:]
                return self.proceed(args)