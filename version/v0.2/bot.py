#############################################################################
# Author: Karim Mamatkazin - nogip@protonmail.com 
# 
# Этот бот был создан специально для моих одноклассников, которым
# (как и мне) надоело искать запись о домашнем задании или объявлении
# в беседе класса.
# Цикл его работы (вкратце): выбирать правильно сформированные сообщения 
# от модераторов и пересылать их всем участникам группы класса.	
# 
# Перед использованием необходимо создать конфиг bot.conf
# (при желании, можно сделать путь до конфига параметром)
#
# Для работы bot.conf должен содержать:
# "group_id" - оттуда будет браться список для рассылки
# "token" - токен группы для авторизации
# "moders" - от кого бот будет принимать сообщения
#
##############################################################################

#!/usr/bin/python3
from vk_api.longpoll import VkLongPoll, VkEventType
import configparser
import logging
import vk_api
import re
import os

# setup logging
_run_dir = '{}/'.format(os.path.split(__file__)[0])
logging.basicConfig(
    format='%(asctime)s|| %(levelname)s:%(lineno)-5d|| %(message)s',
    level=logging.INFO,
    filename=_run_dir + 'bot.log',
    filemode='a')


class Bot:

    def __init__(self, path):
        logging.info('#'*100+'\n'+'-'*100)
        logging.info('Starting initialization...')
        logging.info('Configuration file: ' + path)
        self.config = configparser.ConfigParser()
        self.config.read(path)

        self.token = self.config.get('settings', 'token')
        self.session = vk_api.VkApi(token=self.token)
        self.group_id = self.config.get('settings', 'group_id')
        self.debug = False

        # generations
        self.timetable = self.generate_timetable()
        self.moder_ids = self.generate_moder_ids()
        self.exclude = self.generate_exclude_ids()
        logging.info('Initializaton completed...\n' + '#'*100)

# ----------------------------------------------------------------------------------------------------------------------

    def auth(self):
        try:
            self.session.get_api()
        except vk_api.ApiError as error:
            logging.error(error)

    def set_broadcast_debug(self):
        self.debug = True

    def moder_name(self, moder_id):
        return self.moder_ids.get(moder_id)

# ----------------------------------------------------------------------------------------------------------------------

    def user_info(self, user):
        """ Выдает данные о пользователе вк принимая его id/domain """
        if user == self.group_id:
            return dict(list(self.session.method('groups.getById', {'user_id': user, 'fields': 'domain'}))[0])
        return dict(list(self.session.method('users.get', {'user_ids': user, 'fields': 'domain'}))[0])

    def generate_moder_ids(self):
        """ Генерирует id администраторов(модераторов) из конфига в виде словаря {id:domain} """
        moder_dict = dict()
        moders = self.config.get('settings', 'moders').split(',')
        for moder in moders:
            moder_dict.update({self.user_info(moder).get('id'): moder})
        logging.info('Generated moders ids')
        return moder_dict

    def generate_exclude_ids(self):
        """ Генерирует id исключенных пользователей из конфига """
        exclude_ids = {}
        exclude = self.config.get('settings', 'exclude').split(',')
        for domain in exclude:
            user_id = self.user_info(domain).get('id')
            exclude_ids.update({user_id: domain})
        logging.info('Generated exclude ids')
        return exclude_ids

    def generate_timetable(self):
        """ Генерация расписания из конфига """
        try:
            days = str(self.config.get('timetable', 'workdays')).split(',')
            result = ''
            for day in days:
                result += '==== {day} ====\n'.format(day=day)
                lessons = str(self.config.get('timetable', day)).split(',')
                for lesson in lessons:
                    result += '— {lesson}\n'.format(lesson=lesson)
                result += '\n'
            logging.info('Timetable generated.')
            return result
        except:
            logging.info('TIMETABLE ERROR: [timetable] section does not exist.')

    def update_dests(self):
        """ Обновляет список адресатов. Позволяет добавлять к рассылке пользователей не проводя reboot """
        destinations = {}
        members = dict(self.session.method('groups.getMembers',
                                           {'group_id': self.group_id,
                                            'fields': 'domain'})).get('items')
        for user in members:
            user = dict(user)
            if user.get('id') not in self.exclude:
                destinations.update({user.get('id'): user.get('domain')})
        return destinations

# ----------------------------------------------------------------------------------------------------------------------

    def parse_attachments(self, attachments):
        """ Преобразовывает полученный список вложений в строку (для api) """
        attach = []
        result = ''
        files = dict(attachments)
        amount = 0

        for file in files.keys():
            if str(file).endswith('type'):
                amount += 1
                attach.append((files.get('attach{0}_type'.format(amount)) + files.get('attach{0}'.format(amount))))
        for i in attach:
            result += '{},'.format(i)
        return result

    def broadcast(self, sender, message, attachments, destinations, verbose):
        """ Рассылка """
        if self.debug:  # (debug) participants, (exclude admins) don't receive messages
            destinations = self.moder_ids.keys()
        for client in destinations:
            try:
                user_domain = destinations.get(client)
                if client != sender:
                    self.session.method('messages.send',
                                        {'user_id': client, 'message': message, 'attachment': attachments})
                    logging.info('Message forwarded to @{}'.format(user_domain))
                if client == sender:
                    acknowledge = 'Ok'
                    if verbose:
                        logging.info('Sended acknowledge to sender @{}'.format(self.moder_name(client)))
                        self.session.method('messages.send',
                                        {'user_id': sender, 'message': acknowledge})
            except vk_api.ApiError as error:
                logging.info('ID:{0}; BROADCAST ERROR: {1}'.format(client, error))

# ----------------------------------------------------------------------------------------------------------------------
# in development
    def get_post(self):
        group_id = self.user_info(self.group_id)
        post = self.session.method('wall.get', {'owner_id': group_id})
        print(post)

# ----------------------------------------------------------------------------------------------------------------------

    def send_out(self, accept_phrase, user_id, message, attachments, destinations, verbose=True):
        message = re.sub('{} *$'.format(accept_phrase), '', message).strip()
        logging.info('SEND_OUT: @{user_id} wrote: {text:5}'.format(
            user_id=self.moder_name(user_id),
            text=message))
        self.broadcast(user_id, message, self.parse_attachments(attachments), destinations, verbose=verbose)
        logging.info('-'*61)

    def reply(self, user_id, phrase):
        """ Ответ """
        timetable_accept = ['tmt', 'Tmt']

        if phrase in timetable_accept:
            self.session.method('messages.send', {'user_id': user_id, 'message': self.timetable})
            logging.info('Timetable sended to @{}'.format(user_id))

    def search(self, user_id, message, attachments, event):
        """ Распознавание команд """
        send_accept = 'yes'
        to_moders_accept = 'mdr'

        # если ключевое слово в конце найдено, то разослать
        if user_id in list(self.moder_ids.keys()):
            if re.findall('{} *$'.format(send_accept), message):
                self.send_out(send_accept, user_id, message, attachments, self.update_dests())

            if re.findall('{} *$'.format(to_moders_accept), message):
                self.send_out(to_moders_accept, user_id, message, attachments, self.moder_ids, False)

        if event.to_me:
            self.reply(user_id, message)

    def listen(self):
        """ Основной цикл проверки """
        longpoll = VkLongPoll(self.session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                self.session.method('messages.markAsRead', {'peer_id': event.user_id})
                self.search(event.user_id, event.text, event.attachments, event)

    def start(self):
        self.auth()
        self.listen()

# ----------------------------------------------------------------------------------------------------------------------

    def help(self):
        """ Описание доступных команд """
        pass

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    config_name = 'bot.conf'
    bot = Bot(_run_dir + config_name)
    bot.start()
