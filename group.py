import vk_api

from member import Member
import logging
import os

run_dir = '{}/'.format(os.path.split(__file__)[0])
logging.basicConfig(
    format='%(asctime)s|| %(funcName)20s:%(lineno)-3d|| %(message)s',
    level=logging.INFO,
    filename=run_dir + 'bot.log',
    filemode='w')


class Group:

    def __init__(self, group_id, token):
        self.vk = vk_api.VkApi(token=token)
        self.group_id = group_id

        self.admins = []
        self.admins_len = 0

        self.members = []
        self.members_len = 0

        self.exclude = []
        self.debug = False

    def auth(self):
        try:
            self.vk.get_api()
        except vk_api.ApiError as error:
            logging.info(error)

    def set_broadcast_debug(self):
        self.debug = True

    def set_exclude(self, exclude):
        self.exclude = exclude

    def get_info_by_id(self, user_id):
        for member in self.members:
            if user_id == member.get_info().get('id'):
                return member.get_info()

    def convert_domains(self, domains):
        ids = []
        users = list(self.vk.method('users.get', {'user_ids': domains}))
        for user in users:
            ids.append(user.get('id'))
        return ids

    def get_list_ids(self, lists):
        ids = []
        if lists is 'admins':
            lists = self.admins
        if lists is 'members':
            lists = self.members
        for member in lists:
            ids.append(member.get_info().get('id'))
        return ids

    def add_member(self, member, lists):
        if lists is 'admins':
            self.admins.append(member)
        if lists is 'members':
            self.members.append(member)

    def configure_users(self, items, lists):
        for user in items.get('items'):
            if user.get('id') not in self.exclude:
                member = Member()
                member.configure(**user)
                self.add_member(member, lists)

    def members_update(self):
        """ Обновляет список адресатов. Позволяет добавлять к рассылке пользователей не проводя reboot """
        fields = 'domain'
        members = self.vk.method('groups.getMembers', {'group_id': self.group_id, 'fields': fields})
        if self.members_len != members.get('count'):
            self.members = []
            self.configure_users(members, lists='members')
            self.members_len = members.get('count')

        admins = self.vk.method('groups.getMembers',
                                {'group_id': self.group_id, 'fields': fields, 'filter': 'managers'})
        if self.admins_len != admins.get('count'):
            self.admins = []
            self.configure_users(admins, lists='admins')
            self.admins_len = admins.get('count')
        logging.info('Members list updated...')

    def send(self, send_to, message, attachments):
        self.vk.method('messages.send',
                       {'user_id': send_to, 'message': message, 'attachment': attachments})
