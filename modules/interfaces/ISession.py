from abc import ABCMeta, abstractmethod


class ISession(metaclass=ABCMeta):

    @abstractmethod
    def handle_commands(self, command):
        pass

    @abstractmethod
    def loop(self):
        pass