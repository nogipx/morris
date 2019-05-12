from vk_api.longpoll import VkLongPoll, VkEventType
import logging
import datetime
import re


class DialogHandler:

    def __init__(self, group_manager, command_observer):
        super().__init__()
        self.group = group_manager
        self.longpoll = group_manager.get_longpoll()
        self.command_observer = command_observer

    def listen(self):
        """Listen vk events."""
        try:
            for event in self.longpoll.listen():
                if event.user_id and event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.group.api.messages.send(user_id=event.user_id, message='Доступные команды:', keyboard=self.command_observer.keyboard)
                    self.group.api.messages.markAsRead(peer_id=event.user_id)
                    payload = {'button': ''}
                    if 'payload' in event.extra_values:
                        payload = event.extra_values['payload']
                    print(payload)
                    self.command_observer.execute(event.user_id, event.text, event.attachments, self.group,
                        message_id=event.message_id, payload=payload)

        except ConnectionError:
            logging.error("[!] Lied down. Updating longpoll.. {}".format(datetime.datetime.today()))
            self.longpoll.update_longpoll_server()

