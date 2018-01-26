from threading import Thread

import vk_api
import logging

from modules.group_manager.UsersDatabase import UsersDatabase
from modules.group_manager.data_types.User import User
from modules.interfaces.IGroupManager import IGroupManager
from modules.interfaces.ICommand import ICommand
from modules.group_manager.DBProxy import DBProxy
from modules.group_manager.UserORM import Member


class GroupManager(IGroupManager):

    def __init__(self):
        super().__init__()
        self._storage = DBProxy(Member)

    def auth(self, token):
        try:
            self._vk = vk_api.VkApi(token=token)
        except vk_api.ApiError as error:
            logging.info(error)
        self.setup()

    def setup(self):
        self._setup_group()
        self.update_members()

    def set_exclude_ids(self, exclude):
        self._exclude = exclude

    def get_members_ids(self, admins=False):
        ids = self._storage.get_users_ids(admins=admins)
        return ids

    def send(self, user_id, message, attachments):
        send_to = int(user_id)
        self._vk.method('messages.send', {
            'user_id': send_to,
            'message': message,
            'attachment': self.parse_attachments(attachments)
        })

    def broadcast(self, users_ids, message, attachments):
        for user_id in users_ids:
            try:
                self._vk.method("messages.send", {
                    'user_id': user_id,
                    "message": message,
                    "attachments": self.parse_attachments(attachments)
                })
            except vk_api.VkApiError as error:
                print('{}: {}'.format(user_id, error))

    def get_api(self):
        return self._vk

    def update_members(self):
        fields = 'domain'

        def api_get_members(vk, **kwargs):
            return vk.method('groups.getMembers', kwargs)

        admins = api_get_members(self._vk, group_id=self.group_id, fields=fields, filter='managers')
        self._configure_users(admins)
        members = api_get_members(self._vk, group_id=self.group_id, fields=fields)
        self._configure_users(members)

    def _setup_group(self):
        group = dict(list(self._vk.method('groups.getById'))[0])
        self._group_domain = group.get("screen_name")
        self.group_id = group.get("id")

    def _configure_users(self, items, exclude=list()):
        users = []
        for user in items.get('items'):
            if user.get('id') not in exclude:
                member = User()
                member.configure(**user)
                users.append(member)
        self._storage.update(users)

    def parse_attachments(self, attachments):
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
