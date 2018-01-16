import vk_api

from modules.group_manager.data_types.User import User
from modules.group_manager.interfaces.IGroupManagerImplement import \
    IGroupManagerImplement
import logging


class GroupManager(IGroupManagerImplement):

    def __init__(self):
        self.admins = []
        self.admins_len = 0

        self.members = []
        self.members_len = 0

        self._exclude = []

    def auth(self, token):
        try:
            self._vk = vk_api.VkApi(token=token)
        except vk_api.ApiError as error:
            logging.info(error)
        self.setup()

    def setup(self):
        self.setup_group()
        self.update_members()

    def set_exclude_ids(self, exclude):
        self._exclude = exclude

    def get_members(self, category):
        if category is 'admins':
            return self.admins
        if category is 'members':
            return self.members

    def update_members(self):
        fields = 'domain'

        members = self._vk.method('groups.getMembers',
                                  {'group_id': self._group_domain,
                                   'fields': fields})
        if self.members_len != members.get('count'):
            self.members = []
            self.configure_users(members, lists='members')
            self.members_len = members.get('count')

        admins = self._vk.method('groups.getMembers',
                                 {'group_id': self._group_domain,
                                  'fields': fields,
                                  'filter': 'managers'})
        if self.admins_len != admins.get('count'):
            self.admins = []
            self.configure_users(admins, lists='admins')
            self.admins_len = admins.get('count')
        logging.info('Members list updated...')

    def send(self, send_to, message, attachments):
        send_to = int(send_to)
        self._vk.method('messages.send', {
            'user_id': send_to,
            'message': message,
            # 'attachment': attachments
        })

    def broadcast(self, category, message, attachments):
        for user in self.get_members(category):
            try:
                self._vk.method("messages.send", {
                    'domain': user.domain,
                    "message": message,
                    "attachments": attachments
                })
            except:
                pass

    def get_api(self):
        return self._vk

    def get_members_ids(self, category):
        members = self.get_members(category)
        ids = []
        for member in members:
            ids.append(member.id)
        return ids

    def setup_group(self):
        group = dict(list(self._vk.method('groups.getById'))[0])
        self._group_domain = group.get("screen_name")
        self.group_id = group.get("id")

    def get_by_id(self, user_id):
        for member in self.members:
            if user_id == member.id:
                return member.get_info()

    def convert_domains(self, domains):
        ids = []
        users = list(self._vk.method('users.get', {'user_ids': domains}))
        for user in users:
            ids.append(user.id)
        return ids

    def add_member(self, member, lists):
        if lists is 'admins':
            self.admins.append(member)
        elif lists is 'members':
            self.members.append(member)

    def configure_users(self, items, lists):
        for user in items.get('items'):
            if user.get('id') not in self._exclude:
                member = User()
                member.configure(**user)
                self.add_member(member, lists)
