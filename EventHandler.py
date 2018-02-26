from vk_api.longpoll import VkLongPoll, VkEventType
from collections import deque
from threading import Thread
import re


class EventHandler:

    def __init__(self):
        self._longpoll = None
        self.admin_kw = 'mdr'
        self.members_kw = 'all'
        self._locked_users = []
        self._broadcast_queue = deque()
        self._dialogs_in_thread = []

    def set_group(self, api):
        self._group = api
        self._set_longpoll(self._group.get_api())

    def _set_longpoll(self, group_api):
        self._longpoll = VkLongPoll(group_api)

    def set_command_observer(self, api):
        self._observer = api

    def set_command_checker(self, api):
        self._checker = api

    def lock_user(self, user_id):
        if user_id not in self._locked_users:
            self._locked_users.append(user_id)

    def unlock_user(self, user_id):
        self._locked_users.remove(user_id)

    def listen(self):
        for event in self._longpoll.listen():
            if event.user_id not in self._locked_users and event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self._group.get_api().method('messages.markAsRead', {'peer_id': event.user_id})
                self.handle_event(event.user_id, event.text, event.attachments)

    def handle_event(self, user_id, message, attachments):
        admins_ids = self._group.get_members_ids(admins=True)

        def search(kw):
            return re.search('{} *$'.format(kw), message)

        def sub(kw):
            return re.sub('{} *$'.format(kw), message)

        destination = []
        if search(self.admin_kw):
            destination = admins_ids
            message = sub(self.admin_kw)
        elif search(self.members_kw):
            destination = self._group.get_members_ids()
            message = sub(self.members_kw)

        if user_id in admins_ids and destination:
            broadcast = Thread(target=self._group.broadcast,
                               args=(destination, message, attachments))
            self._broadcast_queue.append(broadcast)
        else:
            member = self._group.get_member(user_id)
            self.lock_user(member.id)
            response = self._observer.execute(member, message, unlock=self.unlock_user)
            if response == 'IGNORE':
                return
            if response:
                self._group.get_api().method('messages.setActivity', {
                    'user_id': user_id,
                    'type': 'typing'
                })
                self._group.send(user_id, response, attachments)
                self.unlock_user(member.id)

if __name__ == '__main__':
    handler = EventHandler()
    handler.lock_user(257408307)
    print(handler._locked_users)
    handler.unlock_user(257408307)
    print(handler._locked_users)

