from abc import ABCMeta, abstractmethod


class IShell(metaclass=ABCMeta):

    # @abstractmethod
    # def shell_init(self, group, user):
    #     pass

    @abstractmethod
    def shell_parse(self, row_input):
        pass

    @abstractmethod
    def shell_execute(self, **kwargs):
        pass