from vk_api.longpoll import VkLongPoll, VkEventType
from collections import deque
from threading import Thread
import re
import datetime

from core.handlers.Handler import Handler
from core.observers.CommandObserver import CommandObserver


class ChatHandler(Handler):

    def __init__(self, group_manager, command_observer):
        super().__init__()

        self.longpoll = group_manager.get_longpoll()
        self.group = group_manager
        self.api = group_manager.get_api()
        self.command_observer = command_observer

        self._locked_users = []
        self._dialogs_in_thread = []
        
    def _lock_user(self, user_id):
        if user_id not in self._locked_users:
            self._locked_users.append(user_id)

    def _unlock_user(self, user_id):
        self._locked_users.remove(user_id)

    def run(self):
        self.listen()

    def listen(self):
        try:
            for event in self.longpoll.listen():

                if event.user_id and event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.group.api.messages.markAsRead(peer_id=event.user_id)
                    self.handle(event.user_id, event.text, event.attachments)

        except ConnectionError:

            print("I HAD BEEN DOWNED IN {}".format(datetime.datetime.today()))
            self.longpoll.update_longpoll_server()

            pass

    def handle(self, user_id, message, attachments):
        member = self.group.get_member(user_id)
        self._lock_user(member.id)
        self.command_observer.execute(member, message, attachments, self.group, unlock=self._unlock_user)
