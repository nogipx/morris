from modules.ege_tasker.interfaces.ISession import ISession
from vk_api.longpoll import VkLongPoll, VkEventType


class Session(ISession):

    def __init__(self, group):
        self._welcome = True
        self._group = group
        self._longpoll = VkLongPoll(self._group.get_api())

    def handle_commands(self, command):
        commands = {
            ''
        }

    def loop(self):
        for event in self._longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                print(event.text)

                if event.text in ['exit', 'end', 'done', 'ok']:
                    self._group.send(event.user_id, self.exit_message(), None)
                    break

                if event.text:
                    self._group.send(event.user_id, self.handle_commands(event.text), None)

    def exit_message(self):
        return 'Setup stoped. Goodbye!'