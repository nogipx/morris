from modules.group_manager.GroupManager import GroupManager
from BotAccount import BotAccount
from modules.commands.CommandObserver import CommandObserver
from modules.commands.HomeWorkCommand import HomeWorkCommand
from modules.commands.TopicTimetableCommand import TopicTimetableCommand
from modules.ege_tasker.EgeTasker import EgeTasker
from modules.ege_tasker.Session import Session
from vk_api.longpoll import VkLongPoll, VkEventType
import re

# run_dir = '{}/'.format(os.getcwd())
# logging.basicConfig(
#     format='%(asctime)s|| %(funcName)20s:%(lineno)-3d|| %(message)s',
#     level=logging.INFO,
#     filename=run_dir + 'bot.log',
#     filemode='w')

class Bot:

    def __init__(self):
        # self._group = None
        # self._account = None
        # self._observer = None
        pass

    def set_account_api(self, api):
        self._account = api

    def set_group_api(self, api):
        self._group = api

    def set_command_observer(self, api):
        self._observer = api

    def search(self, user_id, message, attachments, event):
        send_accept = 'all'
        to_moders_accept = 'mdr'

        if user_id in list(self._group.get_members_ids('admins')):
            if re.findall('{} *$'.format(send_accept), message):
                message = re.sub('{} *$'.format(send_accept), '', message)
                self._group.broadcast('members', message, attachments)

            elif re.findall('{} *$'.format(to_moders_accept), message):
                message = re.sub('{} *$'.format(to_moders_accept), '', message)
                self._group.broadcast('admins', message, attachments)

            else:
                message = self._observer.command(message)
                if message:
                    self._group.get_api().method('messages.setActivity', {
                        'user_id': event.user_id,
                        'type': 'typing'
                    })
                    self._group.send(user_id, message, attachments)

    def listen(self):
        longpoll = VkLongPoll(self._group.get_api())
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self._group.get_api().method('messages.markAsRead', {'peer_id': event.user_id})

                self.search(event.user_id, event.text, event.attachments, event)


if __name__ == '__main__':
    bot = Bot()

    token = '7134ec6b881f83f140dcbdd6a0e0e3001300a2b9f69bc5d13341d0bf650797564141ed907b2dcf8df1e93'
    group = GroupManager()
    group.auth(token)
    bot.set_group_api(group)

    account = BotAccount.get_account()
    account.auth('89890836967', 'HawkingBH98')
    bot.set_account_api(account)

    observer = CommandObserver.get_command_observer()
    timetable = TopicTimetableCommand(group.group_id, account)
    ege = EgeTasker()
    ege.set_group(group)

    observer.add_commands(timetable, ege)
    bot.set_command_observer(observer)

    # observer.command('ege setup')
    # print(observer.command('ege list'))
    # print('Main_COMMAND:', observer.command('ege help'))

    bot.listen()

