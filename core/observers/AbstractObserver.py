from abc import ABCMeta, abstractmethod


class AbstractObserver(metaclass=ABCMeta):

    def __init__(self):
        self.commands = []

    def add(self, *args):
        for arg in args:
            self.commands.append(arg)

    @staticmethod
    def get_observer(observer):
        if observer.__instance__ is None:
            observer.__instance__ = observer()
        return observer.__instance__

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
