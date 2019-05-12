from abc import ABCMeta, abstractmethod


class AbstractObserver(metaclass=ABCMeta):

    def __init__(self):
        self.commands = []

    def add(self, *args):
        for arg in args:
            self.commands.append(arg)

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
