from vk_api.longpoll import VkLongPoll, VkEventType
from threading import Thread
import re


class Bot:

    def set_account_api(self, api):
        self._account = api

    def set_group_api(self, api):
        self._group = api

    def set_command_observer(self, api):
        self._observer = api

    def set_command_checker(self, api):
        self._checker = api

    def search(self, user_id, message, attachments, event):
        send_accept = 'all'
        to_moders_accept = 'mdr'
        if re.findall('{} *$'.format(send_accept), message):
            if user_id in self._group.get_members_ids(admins=True):
                message = re.sub('{} *$'.format(send_accept), '', message)
                broadcast = Thread(target=self._group.broadcast, args=(
                    self._group.get_members_ids(),
                    message,
                    attachments
                ))
                broadcast.start()

        elif re.findall('{} *$'.format(to_moders_accept), message):
            if user_id in list(self._group.get_members_ids(admins=True)):

                message = re.sub('{} *$'.format(to_moders_accept), '', message)
                broadcast = Thread(target=self._group.broadcast, args=(
                    self._group.get_members_ids(admins=True),
                    message,
                    attachments
                ))
                broadcast.start()

        else:
            message = self._observer.execute(user_id, message)
            if message:
                self._group.get_api().method('messages.setActivity', {
                    'user_id': event.user_id,
                    'type': 'typing'
                })
                self._group.send(user_id, message, attachments)

    def listen(self):
        longpoll = VkLongPoll(self._group.get_api())
        checker = Thread(target=self._checker.execute)
        checker.start()
        checker.join()
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self._group.get_api().method('messages.markAsRead', {'peer_id': event.user_id})
                self.search(event.user_id, event.text, event.attachments, event)
