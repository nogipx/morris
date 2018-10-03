import time

from commands import Command
from threading import Timer, Thread
import datetime
import pickle
import os

FILE_EXT = '.txt'
ENCODING = 'utf-8'

CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
wish_path = os.path.join(CUR_DIR, 'wish')
text_path = os.path.join(CUR_DIR, 'text')

BOYS_HELP = 'help.txt'
BOYS_EXAMPLE = 'example.txt'
PLAN_TEXT = 'plan.txt'
GUIDE_TEXT = 'quide.txt'

GIRLS_HELP = 'girls_help.txt'
WELCOME_TEXT = 'welcome.txt'

BOYS_PLAN_SLEEP = 120
BOYS_HELP_SLEEP = 20
BOYS_EXAMPLE_SLEEP = 160
BOYS_SHOW_SLEEP = 10
DEFAULT_SLEEP = 1

WELCOME_ATTACHMENTS = None

INTERVAL = 5
PREVIEW_LENGTH = 50

ADMINS = [257408307, ]


class March8(Command):

    def __init__(self, group):
        super().__init__()
        self._group = group
        self.triggers = ['/8']
        self.autostart_func = self.start_8_march

    def start_8_march(self):
        self.welcome()
        wishes = Thread(target=self.send_wishes)
        wishes.start()

    def welcome(self):
        self.notify_admins('Рассылка начата, поздравляю!')
        girls = self._group.get_member_ids(sex=1)
        girls_text = self.read_text(WELCOME_TEXT)
        personal_broadcast = Thread(target=self.personal_broadcast, args=(girls, girls_text, WELCOME_ATTACHMENTS))
        personal_broadcast.start()

        boys = self._group.get_member_ids(sex=2)
        boys_text = self.read_text(GUIDE_TEXT)
        self._group.broadcast(boys, boys_text, None)

    def personal_broadcast(self, targets, message, attachments):
        for target in targets:
            girl = self._group.get_member(target)
            name = girl.first_name
            message = message.format(name=name)
            self._group.send(target, name, attachments)

    def send_wishes(self, interval=5, first_wait=2):
        wishes_files = os.listdir(wish_path)
        all_wishes = []

        for wish in wishes_files:
            user_id = wish.split('.')[0]
            data = self.load_wish(user_id)
            all_wishes.append(data)
            print(data)

        all_wishes.reverse()

        ack = 'Твое поздравление только что было получено девочками.'

        girls = self._group.get_member_ids(sex=1)
        time.sleep(first_wait)
        while True:
            now = datetime.datetime.today().timetuple()
            hour = now[3]
            minute = now[4]
            # if (hour == 6 and minute >= 30) or (hour == 7 and minute <= 30):
            if all_wishes:
                wish = all_wishes.pop()
                forward_message_ids = ''

                for msg in wish:
                    msg_id = msg[1][1]
                    forward_message_ids += '{},'.format(msg_id)

                self._group.broadcast(girls, '_'*30, forward=forward_message_ids)
                self.acknowledge(wish[0][1][2], ack, destroy=False)
                time.sleep(interval*60)

            else:
                break

    def notify_admins(self, msg, admins=ADMINS):
        self._group.broadcast(admins, msg)

    def proceed(self, *args, **kwargs):
        user = args[0]
        params = args[2:]

        if user.sex == 2:
            if params:
                self.handle_man_cmd(user, params)
            else:
                self.acknowledge(user.id, self.read_text(BOYS_HELP), BOYS_HELP_SLEEP)

    def handle_man_cmd(self, user, params):
        arg2 = 0
        arg3 = 0
        arg4 = 0
        other_args = []

        arg1 = params[0]
        if len(params) > 1:
            arg2 = params[1]
            if len(params) > 2:
                arg3 = params[2]
                if len(params) > 3:
                    arg4 = params[3]
                    if len(params) > 4:
                        other_args = params[4:]

        if arg1 == 'plan':
            plan = self.read_text(PLAN_TEXT)
            self.acknowledge(user.id, plan, BOYS_PLAN_SLEEP)

        elif arg1 == 'help':
            text = self.read_text(BOYS_HELP)
            self.acknowledge(user.id, text, BOYS_HELP_SLEEP)

        elif arg1 == 'example':
            text = self.read_text(BOYS_EXAMPLE)
            self.acknowledge(user.id, text, BOYS_EXAMPLE_SLEEP)

        elif arg1 == 'set':
            if arg2 == 'last' and arg3:
                status = self.set_last_messages(user.id, arg3, first_name=user.first_name)
                self.acknowledge(user.id, status)

        elif arg1 == 'del':
            status = self.delete_saved_message(user.id, arg2)
            self.acknowledge(user.id, status)

        elif arg1 == 'show':
            result = self.show_messages(user.id)
            self.acknowledge(user.id, result, BOYS_SHOW_SLEEP)

        elif arg1 == 'clear':
            self.delete_wish(user.id)
            self.acknowledge(user.id, 'Очищено')

        elif arg1 == 'look':
            self.look_wish_preview(user.id, user.id)

        elif arg1 == 'admin' and user.id in ADMINS:
            if arg2 == 'show':
                if arg3:
                    wishes = self.admin_show_wish(arg3)
                else:
                    wishes = self.admin_show_wish()
                self.acknowledge(user.id, wishes, BOYS_SHOW_SLEEP)

            elif arg2 == 'del':
                status = self.admin_delete_msg(arg3, arg4)
                self.acknowledge(user.id, status)

            elif arg2 == 'clear':
                status = self.admin_clear_wish(arg3)
                self.acknowledge(user.id, status)

            elif arg2 == 'send':
                boys = self._group.get_member_ids(sex=2)
                if arg3 == 'wishes':
                    self.send_wishes(1, 1)
                    self.acknowledge(user.id, 'Wishes sent')

                elif arg3 == 'motivation':
                    text = self.read_text(BOYS_EXAMPLE)
                    self._group.broadcast(boys, text, destroy=True, destroy_type=0)
                    self.acknowledge(user.id, 'Motivation sent')

                elif arg3 == 'msg':
                    if arg4 == 'all':
                        text = ''
                        for word in other_args:
                            text += '{} '.format(word)
                        self._group.broadcast(boys, text, destroy=True, destroy_type=0)

    def admin_show_wish(self, index=None):
        index = self.normal_index(index)

        if index is not None and index >= 0:
            wish_author_id = self.get_author_id_by_index(index)
            if wish_author_id:
                return self.show_messages(wish_author_id)
            else:
                return 'Bad index.'

        else:
            result = ''
            wish_files = os.listdir(wish_path)
            for i, filename in enumerate(wish_files):
                wish_author_id = filename.split('.')[0]
                wish = self.load_wish(wish_author_id)
                if wish:
                    author_name = wish[0][1][3]
                    count_messages = len(wish)
                    result += '{}) {:<10} - {}\n'.format(i+1, author_name, count_messages)
                else:
                    return "Empty."
            return result

    def admin_delete_msg(self, index, message_index):
        index = self.normal_index(index)
        message_index = self.normal_index(message_index)

        wish_author_id = self.get_author_id_by_index(index)
        if wish_author_id:
            wish = self.load_wish(wish_author_id)
            wish.pop(message_index-1)
            self.save_wish(wish_author_id, wish)
            return "Deleted."
        else:
            return "Bad index."

    def admin_clear_wish(self, index):
        index = self.normal_index(index)
        wish_author_id = self.get_author_id_by_index(index)
        self.delete_wish(wish_author_id)
        return 'Cleared.'

    def delete_saved_message(self, user_id, index):
        index = self.normal_index(index)

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
        return "Удалено."

    def acknowledge(self, user_id, msg='', sleep=DEFAULT_SLEEP,
                    attachments=None, forward=None, destroy=True, delete_for_all=True):
        if destroy:
            msg = msg + '\nСообщение будет удалено через {} сек.'.format(sleep)
            self._group.send(user_id, msg, attachments=attachments, forward=forward)

            accept_msg_id = self._group.method('messages.getHistory', {
                'peer_id': user_id,
                'count': 1
            }).get('items')[0].get('id')

            if delete_for_all:
                for_all = 1
            else:
                for_all = 0

            timer = Timer(float(sleep), self._group.delete, args=(accept_msg_id, for_all))
            timer.start()

        else:
            self._group.send(user_id, msg)

    def set_last_messages(self, user_id, count, first_name='', preview=PREVIEW_LENGTH):
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
            text = msg.get('body')[:preview]

            if msg.get('attachments'):
                text += '+ Вложение'

            msg_info = [i+1, (text, msg_id, user_id, first_name)]
            result.insert(i, msg_info)

        self.save_wish(user_id, result)
        return 'OK'

    def show_messages(self, user_id):
        wish = self.load_wish(user_id)

        if not wish:
            return 'Пусто.'

        result = ''
        for i, msg in enumerate(wish):
            text = msg[1][0].split('\n')[0].strip()
            text_id = msg[1][1]

            result += '{i}) {text:20}{dots} - id({text_id})\n'.format(
                i=i+1, text=text, text_id=text_id, dots='...' if len(text) > PREVIEW_LENGTH else '')
        if not result:
            result = 'Пусто.'

        return result

    def look_wish_preview(self, owner_id, receiver):
        wish = self.load_wish(owner_id)
        forward_message_ids = ''
        if wish:
            for msg in wish:
                msg_id = msg[1][1]
                forward_message_ids += '{},'.format(msg_id)
            self.acknowledge(receiver, forward=forward_message_ids, sleep=BOYS_SHOW_SLEEP)
        else:
            self.acknowledge(owner_id, 'Empty.')

    def save_wish(self, user_id, message_ids, extension=FILE_EXT):
        filename = str(user_id) + extension
        file_path = os.path.join(wish_path, filename)

        if os.path.exists(file_path):
            self.delete_wish(user_id)

        with open(file_path, 'wb') as file:
            pickle.dump(message_ids, file)

    @staticmethod
    def read_text(name, path=text_path):
        file_path = os.path.join(path, name)
        text = ''

        with open(file_path, 'r', encoding=ENCODING) as file:
            for row in file.readlines():
                text += row

        return text

    @staticmethod
    def load_wish(user_id, extension=FILE_EXT):
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

    @staticmethod
    def delete_wish(user_id, extension=FILE_EXT):
        filename = str(user_id) + extension
        file_path = os.path.join(wish_path, filename)
        os.remove(file_path)

    @staticmethod
    def normal_index(index):
        if index:
            if not isinstance(index, int):
                try:
                    return int(index)-1
                except TypeError:
                    return ''

    @staticmethod
    def get_author_id_by_index(index):
        wish_files = os.listdir(wish_path)
        if isinstance(index, int) and index <= len(wish_files)-1:
            wish_author_id = wish_files[index].split('.')[0]
            return wish_author_id
        else:
            return None
