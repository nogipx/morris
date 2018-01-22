from modules.group_manager.GroupManager import GroupManager
from BotAccount import BotAccount
from modules.commands.CommandObserver import CommandObserver
from modules.interfaces.IObserver import IObserver
from modules.commands.EgeShellCommand import EgeShellCommand
from modules.commands.TopicTimetableCommand import TopicTimetableCommand
from vk_api.longpoll import VkLongPoll, VkEventType
from modules.notify_checker.UntillEge import UntillEge
from modules.notify_checker.NotifyCheckObserver import NotifyCheckerObserver
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

    @staticmethod
    def parse_attachments(attachments):
        attach = []
        result = ''
        files = attachments
        amount = 0

        for file in files.keys():
            if str(file).endswith('type'):
                amount += 1
                attach.append((files.get('attach{0}_type'.format(amount)) + files.get('attach{0}'.format(amount))))
        for i in attach:
            result += '{},'.format(i)
        return result

    def search(self, user_id, message, attachments, event):
        send_accept = 'all'
        to_moders_accept = 'mdr'

        if re.findall('{} *$'.format(send_accept), message):
            if user_id in list(self._group.get_moders_ids()):

                message = re.sub('{} *$'.format(send_accept), '', message)
                self._group.broadcast(
                    self._group.get_members(),
                    message,
                    self.parse_attachments(attachments))

        elif re.findall('{} *$'.format(to_moders_accept), message):
            if user_id in list(self._group.get_moders_ids()):

                message = re.sub('{} *$'.format(to_moders_accept), '', message)
                self._group.broadcast(
                    self._group.get_members(admins=True),
                    message,
                    self.parse_attachments(attachments))

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
        p = Thread(target=self._checker.loop)
        p.start()
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self._group.get_api().method('messages.markAsRead', {'peer_id': event.user_id})
                self.search(event.user_id, event.text, event.attachments, event)


if __name__ == '__main__':
    bot = Bot()

    # Creating group-class
    group = GroupManager()
    group.auth(token)
    bot.set_group_api(group)

    # Setup account for bot. This is need for parsing group wall and timetable
    account = BotAccount.get_account()
    account.auth(login, password)
    bot.set_account_api(account)

    # Setup observers that handle commands
    command_observer = IObserver.get_observer(CommandObserver)
    notify_observer = IObserver.get_observer(NotifyCheckerObserver)
    notify_observer.set_group(group)

    # Setup commands
    timetable = TopicTimetableCommand(group.group_id, account)
    ege = EgeShellCommand(group)
    untill_ege = UntillEge('18-05-28')

    # Adding command modules in particular handlers(observers)
    command_observer.add_items(timetable, ege, untill_ege)
    notify_observer.add_items(untill_ege, timetable)

    # Adding observers into bot
    bot.set_command_observer(command_observer)
    bot.set_command_checker(notify_observer)

    # Start mainloop
    bot.listen()
