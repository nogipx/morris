import logging

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
        self.active_dialogs = {}

    def run(self):
        self.listen()

    def listen(self):
        try:
            for event in self.longpoll.listen():
                if event.user_id and event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.group.api.messages.markAsRead(peer_id=event.user_id)
                    self.handle(event.user_id, event.text, event.attachments, message_id=event.message_id)

        except ConnectionError:
            logging.error("I HAD BEEN DOWNED IN {}".format(datetime.datetime.today()))
            self.longpoll.update_longpoll_server()

    def start_dialog(self, user_id, message, attachments):
        pass
        # t = Thread(target=self.handle, args=(user_id, message, attachments))
        # self.active_dialogs.update({user_id: t})
        # t.setName(user_id)
        # t.start()

    def end_dialog(self, user_id):
        pass

    def handle(self, user_id, message, attachments, **kwargs):
        member = self.group.get_member(user_id)
        # self._lock_user(member.id)
        self.group.update_members()
        self.command_observer.execute(member, message, attachments, self.group, **kwargs)

