from abc import ABCMeta, abstractmethod


class ICommandObserver(metaclass=ABCMeta):

    @abstractmethod
    def add_commands(self, *args):
        pass

    @abstractmethod
    def command(self, cmd):
        pass
