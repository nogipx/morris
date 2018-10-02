from commands.interface import IShell
from vk_api.longpoll import VkLongPoll, VkEventType


class EgeShell(IShell):

    __commands__ = []

    def __init__(self, group, user):
        self._group = group
        self._user = user
        self._longpoll = VkLongPoll(self._group.get_api())

    def shell_parse(self, row_input):
        super().shell_parse(row_input)

    def shell_execute(self, *args):
        print("THREAD_USER", args)
        self.greeting_message()
        for event in self._longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self._group.get_api().method('messages.markAsRead', {'peer_id': event.user_id})
                if event.text in ['exit', 'Exit']:
                    # TODO сделать адекватную блокировку и проверку id пользоваьеля
                    # не нормально то, что блокировка потока снимается не в том же классе, в которой установилась
                    # сообщение выхода разошлется даже если сессия не запускалась
                    self.exit_message()
                    return False

    def greeting_message(self):
        greet_msg = 'Добрый день {}. \n' \
                    'Открыта сессия задачника ЕГЭ. \n' \
                    '"exit" для завершения. \n\n'.format(self._user.get_name())

        greet_msg += 'Доступные команды: \n' \
                     ''
        self._group.send(self._user.id, greet_msg, None)

    def exit_message(self):
        exit_msg = 'Сессия завершена. Удачи!'
        self._group.send(self._user.id, exit_msg, None)
