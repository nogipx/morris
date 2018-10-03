from abc import ABCMeta, abstractmethod


class AbstractObserver(metaclass=ABCMeta):

    __instance__ = None

    def __init__(self):
        self.commands = []

    def add(self, *args):
        for arg in args:
            self.commands.append(arg)

    @classmethod
    def get_observer(cls):
        if cls.__instance__ is None:
            cls.__instance__ = cls()
        return cls.__instance__

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
