from abc import ABCMeta, abstractmethod


class IObserver(metaclass=ABCMeta):

    def __init__(self):
        self._commands = []

    @staticmethod
    def get_observer(observer):
        if observer.__instance__ is None:
            observer.__instance__ = observer()
        return observer.__instance__

    def add_items(self, *args):
        for arg in args:
            self._commands.append(arg)

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
