from abc import ABCMeta, abstractmethod


class IGroupManagerImplement(metaclass=ABCMeta):

    @abstractmethod
    def auth(self, token):
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def update_members(self):
        pass

    @abstractmethod
    def get_members(self, category):
        pass

    @abstractmethod
    def set_exclude_ids(self, exclude):
        pass

    @abstractmethod
    def send(self, destination, message, attachments):
        pass

    @abstractmethod
    def broadcast(self, category, message, attachments):
        pass

    @abstractmethod
    def get_api(self):
        pass
