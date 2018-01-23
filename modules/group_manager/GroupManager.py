from threading import Thread

import vk_api

from modules.group_manager.data_types.User import User
from modules.interfaces.IGroupManagerImplement import IGroupManagerImplement
from modules.group_manager.UsersStorage import UsersStorage
import logging


class GroupManager(IGroupManagerImplement):

    def __init__(self):
        self._storage = UsersStorage.get_storage()

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

    def get_members(self, admins=False):
        return self._storage.get_users(admins)

    def send(self, user_id, message, attachments):
        send_to = int(user_id)
        self._vk.method('messages.send', {
            'user_id': send_to,
            'message': message,
            'attachment': attachments
        })

    def broadcast(self, users, message, attachments):
        for user in users:
            try:
                self._vk.method("messages.send", {
                    'domain': user.domain,
                    "message": message,
                    "attachments": attachments
                })
            except vk_api.VkApiError as e:
                pass

    def get_api(self):
        return self._vk

    def update_members(self):
        fields = 'domain'

        def api_get_members(vk, **kwargs):
            return vk.method('groups.getMembers', kwargs)

        admins = api_get_members(self._vk, group_id=self.group_id, fields=fields, filter='managers')
        self._configure_users(self._storage, admins)
        members = api_get_members(self._vk, group_id=self.group_id, fields=fields)
        self._configure_users(self._storage, members)

    def _configure_users(self, storage, items, exclude=list()):
        for user in items.get('items'):
            if user.get('id') not in exclude:
                member = User()
                member.configure(**user)
                storage.add_user(member)

    def _get_moders_ids(self):
        return self._storage.admins_ids

    def _setup_group(self):
        group = dict(list(self._vk.method('groups.getById'))[0])
        self._group_domain = group.get("screen_name")
        self.group_id = group.get("id")
