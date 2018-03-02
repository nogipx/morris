import time

from modules.commands.interface.ICommand import ICommand
from modules.database.DBProxy import DBProxy


class March8(ICommand):
    def welcome(self):
        self.notify_admin('Рассылка начата, поздравляю!')
        destinations = self._group.get_members_ids(sex=1)
        text = ''
        with open('welcome.txt', 'r') as file:
            file.close()
            text = file.read()
        # self._group.broadcast(destinations, text, None)
        self.notify_admin(text)

    def notify_admin(self, msg, me=257408307):
        self._group.send(msg, me)

    def __init__(self, group):
        super().__init__()
        self._triggers = ['/8']
        self._group = group
        self.messages = []
        self.already_welcome = False

    def proceed(self, *args, **kwargs):
        if not self.already_welcome:
            self.welcome()
            self.already_welcome = True
        else:
            return

        user = args[0]
        command = args[1]
        params = args[2:]
        if params:
            if user.sex == 1:
                self.handle_woman_cmd(user, params)

            if user.sex == 2:
                self.handle_man_cmd(user, params)

    def handle_woman_cmd(self, user, params):

        arg1 = params[0]
        if arg1 == 'любимые':
            pass
        if arg1 == 'красивая':
            pass
        if arg1 == 'помощь':
            pass

    def handle_man_cmd(self, user, params):
        arg2 = 0
        arg3 = 0

        arg1 = params[0]
        if len(params) > 1:
            arg2 = params[1]
            if len(params) > 2:
                arg3 = params[2]

        if arg1 == 'add':
            if arg2 == 'last' and arg3:
                self.set_last_messages(user.id, arg3)

        elif arg1 == 'del':
            status = self.delete_saved_message(user.id, arg2)
            self.send_output(status, user.id)

        elif arg1 == 'show':
            result = self.get_saved_messages()
            self.send_output(result, user.id, sleep=10)

        elif arg1 == 'help':
            plan = self.get_plan()
            self.send_output(plan, user.id)

    def delete_saved_message(self, index):
        index = int(index)
        self.messages.pop(index)
        for i in range(index, len(self.messages)):
            self.messages[i+1][0] = i+1
            self.messages[i] = self.messages[i+1]
        return "Deleted"

    def send_output(self, msg, user_id, sleep=1):
        msg = msg + '\nСообщение будет удалено через {} сек.'.format(sleep)
        self._group.send(user_id, msg, None)
        accept_msg_id = self._group.method('messages.getHistory', {
            'peer_id': user_id,
            'count': 1
        }).get('items')[0].get('id')

        time.sleep(sleep)
        self._group.delete(accept_msg_id)

    def set_last_messages(self, user_id, count):
        messages = self._group.method('messages.getHistory', {
            'peer_id': user_id,
            'count': count
        }).get('items')

        for i, msg in enumerate(messages):
            msg_id = msg.get('id')
            text = msg.get('body')[:30]
            if msg.get('attachments'):
                text += '+ Вложение'

            self.messages.insert(i, (text, msg_id))
        return 'OK'

    def get_saved_messages(self):
        result = ''
        for i, msg in enumerate(self.messages):
            result += '{}) {:>20}... - id({})\n'.format(i+1, str(msg[0]), str(msg[1]))
        return result
