#!/usr/bin/python3
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
#
##############################################################################
from vk_api.longpoll import VkLongPoll, VkEventType
import logging

import configparser
import argparse
import vk_api
import re
import os

from files.group import Group
from files.post_manager import PostManager
from files.generators import timetable_from_config

run_dir = '{}/'.format(os.path.split(__file__)[0])

logging.basicConfig(
    format='%(asctime)s|| %(funcName)20s:%(lineno)-3d|| %(message)s',
    filename=run_dir + 'bot.log',
    filemode='a')


def parse_attachments(attachments):
    """ Преобразовывает полученный список вложений в строку (для api) """
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


class Bot:

    def __init__(self, path):
        self.five_days = False
        self.debug = False

        logging.info('Configuration file: ' + path)
        self.config = configparser.ConfigParser()
        if not os.path.exists(path):
            self.generate_config(path)
        self.config.read(path)

        # Group configures
        token = self.config.get('settings', 'token')
        self.group_id = self.config.get('settings', 'group_id')
        self.group = Group(self.group_id, token)
        self.group.set_exclude(self.generate_exclude_ids())
        self.group.members_update()

        # Posts analyzer configures
        post_login = self.config.get('posts_parser', 'login')
        post_password = self.config.get('posts_parser', 'password')
        self.manager = None
        if post_login and post_password:
            self.manager = PostManager(post_login, post_password, self.group_id)

        # Timetable configures
        self.timetable = timetable_from_config(self.config)

    def generate_config(self, path):
        # settings config
        self.config.add_section('settings')
        self.config.set('settings', 'token', '')
        self.config.set('settings', 'group_id', '')
        self.config.set('settings', 'exclude', '')

        # timetable config
        self.config.add_section('timetable')
        work_days = ''
        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
        if self.five_days:
            days = days[:-1]
        for day in days:
            self.config.set('timetable', day, '')
            work_days += '{},'.format(day)
        self.config.set('timetable', 'work_days', work_days[:-1])

        # group_bot config
        self.config.add_section('posts_parser')
        self.config.set('posts_parser', 'login', '')
        self.config.set('posts_parser', 'password', '')

        with open(path, 'w') as config_file:
            self.config.write(config_file)

    def generate_exclude_ids(self):
        """ Генерирует id исключенных пользователей из конфига """
        exclude = self.config.get('settings', 'exclude')
        if exclude:
            exclude_ids = self.group.convert_domains(exclude)
            logging.info('Generated exclude ids')
            return exclude_ids
        return []

    def reply(self, user_id, command, attachments):
        """ Ответ """
        timetable_accept = ['tt', 'Tt']
        homework_accept = ['hw', 'Hw']
        domain = self.group.get_info_by_id(user_id).get('domain')
        message = ''

        if command in timetable_accept:
            message = self.timetable
            logging.info('Timetable sended to @{}'.format(domain))

        elif command in homework_accept and self.manager is not None:
            message = self.manager.week()
            logging.info('Homework for week sended to @{}'.format(domain))

        if message:
            self.group.send(send_to=user_id, message=message, attachments=attachments)

    def broadcast(self, accept_phrase, user_id, message, destinations, attachments):

        message = re.sub('{} *$'.format(accept_phrase), '', message).strip()

        logging.info('BROADCAST: @{domain} written: {text:5}'.format(
            domain=self.group.get_info_by_id(user_id).get('domain'),
            text=message))

        if accept_phrase == 'mdr':
            message += '@{}\n\n'.format(self.group.get_info_by_id(user_id).get('first_name'))

        self.send_out(user_id, message, destinations, attachments)
        logging.info('-'*60)

    def send_out(self, sender, message, destinations, attachments):
        """ Рассылка """

        self.group.members_update()

        if self.debug:  # (debug) participants, (exclude admins) don't receive messages
            destinations = self.group.get_list_ids('admins')

        for client in destinations:
            try:

                if client != sender:
                    self.group.send(send_to=client, message=message, attachments=attachments)
                    logging.info('SENDED TO: {} {}'.format(self.group.get_info_by_id(client).get('first_name'),
                                                           self.group.get_info_by_id(client).get('last_name')))

                if client == sender:
                    acknowledge = 'Ok'
                    self.group.send(send_to=client, message=acknowledge, attachments='')

            except vk_api.ApiError as error:
                logging.info('ID:{0}; BROADCAST ERROR: {1}'.format(client, error))

    def search(self, user_id, message, attachments, event):
        """ Распознавание команд """

        send_accept = 'all'
        to_moders_accept = 'mdr'

        # если ключевое слово в конце найдено, то разослать
        if user_id in list(self.group.get_list_ids('admins')):
            user_id = self.group.get_info_by_id(user_id).get('id')

            if re.findall('{} *$'.format(send_accept), message):
                self.broadcast(send_accept, self.group.get_info_by_id(user_id).get('id'), message,
                               self.group.get_list_ids('members'), parse_attachments(attachments))

            if re.findall('{} *$'.format(to_moders_accept), message):
                self.broadcast(to_moders_accept, self.group.get_info_by_id(user_id).get('id'), message,
                               self.group.get_list_ids('admins'), parse_attachments(attachments))

        if event.to_me:
            self.reply(user_id, message, attachments)

    def listen(self):
        """ Основной цикл проверки """
        longpoll = VkLongPoll(self.group.vk)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                self.group.vk.method('messages.markAsRead', {'peer_id': event.user_id})
                self.search(event.user_id, event.text, event.attachments, event)

    def start(self):
        self.group.auth()
        self.listen()

    def help(self):
        """ Описание доступных команд """
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Morris's Bot settings")
    parser.add_argument('path', help='path to config-file or its name')
    path = vars(parser.parse_args()).get('path')
    bot = Bot(path)
    bot.start()
