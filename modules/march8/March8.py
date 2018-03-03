import time

from modules.commands.interface.ICommand import ICommand
from modules.database.DBProxy import DBProxy
import pickle
import os
from threading import Timer

wish_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'wish')
text_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'text')
FILE_EXT = '.txt'
BOYS_HELP = 'help.txt'
BOYS_EXAMPLE = 'example.txt'
PLAN_TEXT = 'plan.txt'
WELCOME_TEXT = 'welcome.txt'
GIRLS_HELP = 'girls_help.txt'

BOYS_PLAN_SLEEP = 120
BOYS_HELP_SLEEP = 20
BOYS_EXAMPLE_SLEEP = 160
BOYS_SHOW_SLEEP = 10
DEFAULT_SLEEP = 1


class March8(ICommand):

    def welcome(self):
        self.notify_admin('Рассылка начата, поздравляю!')
        destinations = self._group.get_member_ids(sex=1)
        text = ''
        with open('welcome.txt', 'r') as file:
            file.close()
            text = file.read()
        # self._group.broadcast(destinations, text, None)
        self.notify_admin(text)

    def notify_admin(self, msg, me=257408307):
        self._group.send(me, msg, None)

    def __init__(self, group):
        super().__init__()
        self._group = group
        self.triggers = ['/8']
        self.already_welcome = False
        self.autostart_func = self.welcome

    def proceed(self, *args, **kwargs):
        user = args[0]
        command = args[1]
        params = args[2:]

        if user.sex == 1:
            if params:
                self.handle_woman_cmd(user, params)
            else:
                self.send_output(user.id, self.read_text(GIRLS_HELP), BOYS_HELP_SLEEP)

        if user.sex == 2:
            if params:
                self.handle_man_cmd(user, params)
            else:
                self.send_output(user.id, self.read_text(BOYS_HELP), BOYS_HELP_SLEEP)

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

        if arg1 == 'set':
            if arg2 == 'last' and arg3:
                status = self.set_last_messages(user.id, arg3)
                self.send_output(user.id, status)

        elif arg1 == 'del':
            status = self.delete_saved_message(user.id, arg2)
            self.send_output(user.id, status)

        elif arg1 == 'show':
            result = self.get_saved_messages(user.id)
            self.send_output(user.id, result, BOYS_SHOW_SLEEP)

        elif arg1 == 'plan':
            plan = self.read_text(PLAN_TEXT)
            self.send_output(user.id, plan, BOYS_PLAN_SLEEP)

        elif arg1 == 'help':
            text = self.read_text(BOYS_HELP)
            self.send_output(user.id, text, BOYS_HELP_SLEEP)

        elif arg1 == 'example':
            text = self.read_text(BOYS_EXAMPLE)
            self.send_output(user.id, text, BOYS_EXAMPLE_SLEEP)

        elif arg1 == 'clear':
            self.delete_wish(user.id)
            self.send_output(user.id, 'Очищено')

    def delete_saved_message(self, user_id, index):
        index = int(index)-1

        messages = self.load_wish(user_id)
        if messages:
            messages.pop(index)
        else:
            return "Пусто. Удалять нечего."

        for i in range(index, len(messages)):
            if i == len(messages):
                messages.pop(i)
                break
            messages[i][0] = messages[i][0] - 1

        self.save_wish(user_id, messages)
        return "Deleted"

    def send_output(self, user_id, msg, sleep=DEFAULT_SLEEP):
        msg = msg + '\nСообщение будет удалено через {} сек.'.format(sleep)
        self._group.send(user_id, msg, None)
        accept_msg_id = self._group.method('messages.getHistory', {
            'peer_id': user_id,
            'count': 1
        }).get('items')[0].get('id')

        timer = Timer(float(sleep), self._group.delete, args=(accept_msg_id,))
        timer.start()

    def set_last_messages(self, user_id, count):
        count = str(int(count)+1)
        messages = self._group.method('messages.getHistory', {
            'peer_id': user_id,
            'count': count
        }).get('items')
        messages.pop(0)
        messages.reverse()

        result = []
        for i, msg in enumerate(messages):
            msg_id = msg.get('id')
            text = msg.get('body')[:30]
            if msg.get('attachments'):
                text += '+ Вложение'
            msg_info = [i+1, (text, msg_id)]
            result.insert(i, msg_info)
        self.save_wish(user_id, result)
        return 'OK'

    def get_saved_messages(self, user_id):
        result = ''
        wish = self.load_wish(user_id)
        if not wish:
            return 'Пусто'

        for i, msg in enumerate(wish):
            result += '{}) {:>20}... - id({})\n'.format(i+1, str(msg[1][0]), str(msg[1][1]))
        if not result:
            result = 'Пусто.'

        return result

    def read_text(self, name, path=text_path):
        file_path = os.path.join(path, name)
        text = ''
        file = open(file_path)
        for row in file.readlines():
            text += row
        return text

    def save_wish(self, user_id, message_ids, extension=FILE_EXT):
        filename = str(user_id) + extension
        file_path = os.path.join(wish_path, filename)
        if os.path.exists(file_path):
            self.delete_wish(user_id)
        with open(file_path, 'wb') as file:
            pickle.dump(message_ids, file)

    def load_wish(self, user_id, extension=FILE_EXT):
        filename = str(user_id) + extension
        file_path = os.path.join(wish_path, filename)

        if not os.path.exists(file_path):
            open(file_path, 'w').close()
            return

        with open(file_path, 'rb') as file:
            try:
                data = pickle.load(file)
                return data
            except EOFError:
                pass

    def delete_wish(self, user_id, extension=FILE_EXT):
        filename = str(user_id) + extension
        file_path = os.path.join(wish_path, filename)
        os.remove(file_path)