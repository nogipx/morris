#!/usr/bin/python3
import math
import logging
import configparser
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

logging.basicConfig(
    format='%(asctime)s|| %(levelname)s:%(lineno)-5d|| %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='w')


class Bot:

    def __init__(self, path):
        logging.info('Configuration file: ' + path)
        config = configparser.ConfigParser()
        config.read(path)
        self.token = config.get('settings', 'token')
        self.group_id = config.get('settings', 'group_id')

        self.moder_ids = str(config.get('settings', 'moders')).split(',')
        self.moder_ids = dict([moder.split(':') for moder in self.moder_ids])

        self.exclude = set(config.get('settings', 'exclude').split(','))
        self.session = vk_api.VkApi(token=self.token)
        self.destinations = []

    def auth(self):
        try:
            self.session.get_api()
        except vk_api.ApiError as error:
            logging.error(error)

    def moder_name(self, id):
        return self.moder_ids.get(id)

    def set_moders(self, moders):
        self.moder_ids = moders

    def set_group(self, group_id):
        self.group_id = group_id

    def set_exclude(self, exclude):
        self.exclude = exclude

    def parse_attachments(self, attachments):
        print(attachments)
        attach = []
        result = ''
        j = dict(attachments)
        for i in range(1, int(len(j)/2)+1):
            at_type = 'attach'+str(i)+'_type'
            at_id = 'attach'+str(i)
            #at_key = dict(str(self.session.method('photos.getById', {'photo_id': at_id}))).get('access_key')
            attach.append((j.get(at_type) + j.get(at_id)))
        for i in attach:
            result += '{},'.format(i)
        print(result)
        return result[:-1]

    def convert_exclude(self):
        exclude_ids = []
        for domain in self.exclude:
            id = dict(list(self.session.method('users.get', {'user_ids': domain}))[0]).get('id')
            exclude_ids.append(str(id))
        self.exclude = set(exclude_ids)

    def update_dests(self):
        tmpdst = set()
        members = dict(self.session.method('groups.getMembers',
            {'group_id': self.group_id})).get('items')

        for user in members:
            tmpdst.add(str(user))
        for user in self.exclude:
            try: tmpdst.remove(str(user))
            except: pass
        self.destinations = tmpdst

    def broadcast(self, admin, message, attachments):
        for client in self.destinations:
                try:
                    if client != admin:
                        self.session.method('messages.send',
                                            {'user_id': client, 'message': message, 'attachment': attachments})
                        logging.info('Message forwarded to {}'.format(client))
                    else:
                        message = 'Все сообщения отправлены.'
                        self.session.method('messages.send',
                                            {'user_id': admin, 'message': message, 'attachment': attachments})
                        pass
                except:
                    pass

    def search(self):
        try:
            longpoll = VkLongPoll(self.session)
            accept = 'yes'
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    self.session.method('messages.markAsRead', {'peer_id': event.user_id})
                    if str(event.user_id) in list(self.moder_ids.keys()):
                        message = str(event.text)
                        if message.endswith(accept):
                            logging.log(logging.INFO, 'Moder @{user_id} have written: {text:5}'.format(     # log message
                                user_id=self.moder_name(str(event.user_id)),
                                text=event.text))
                            self.update_dests()
                            message = message[:-len(accept)].rstrip()
                            self.broadcast(str(event.user_id), message, self.parse_attachments(event.attachments))

        except vk_api.ApiError as error:
            logging.info('FATAL ERROR: ' + str(error))

    def start(self):
        self.auth()
        logging.log(logging.INFO, 'Initializaton completed...')
        self.search()

    def init(self):
        self.convert_exclude()


if __name__ == '__main__':
    bot = Bot('test.conf')
    bot.convert_exclude()
    bot.start()
