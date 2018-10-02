import vk_api
import logging

from vk_communicate.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.group_manager.data_types.User import User
from vk_communicate.group_manager import IGroup
from threading import Thread


class Group(BaseCommunicateVK):

    def __init__(self, vksession, storage):
        super().__init__(vksession)
        self.storage = storage

    def set_exclude_ids(self, exclude):
        self._exclude = exclude

    def setup(self):
        self._setup_group()
        self.update_members()

        return self

    def _setup_group(self):
        group = dict(list(self.api.groups.getById())[0])
        self._group_domain = group.get("screen_name")
        self.group_id = group.get("id")

    def update_members(self):
        fields = 'domain, sex'

        admins = self.api.groups.getMembers(group_id=self.group_id, fields=fields, filter='managers')
        self._put_into_storage(self._configure_users(admins))

        members = self.api.groups.getMembers(group_id=self.group_id, fields=fields)
        self._put_into_storage(self._configure_users(members))

        return self

    def _put_into_storage(self, members):
        self.storage.update(members)

    # Было бы лучше, если бы пользователи добавлялись напрямую в бд, а не через дополнительный класс
    @staticmethod
    def _configure_users(items, exclude=None):

        if exclude is None:
            exclude = []

        users = []
        for user in items.get('items'):

            if user.get('id') not in exclude:
                member = User()
                member.configure(**user)
                users.append(member)

        return users

    def get_member_ids(self, admins=False, sex=0):
        ids = self.storage.get_users_ids(admins=admins, sex=sex)

        return ids

    def get_member(self, uid):
        member = self.storage.get_member(uid)
        print(member.id, member.domain)
        user = User()

        for field in member._data:
            user.__setattr__(field, member._data.get(field))

        print(user)

        return user

    def broadcast(self, users_ids, message, attachments=None, forward=None, destroy=False, destroy_type=0):
        if not message:
            return

        def send_all(msg, destroy, delete_for_all):
            for user_id in users_ids:
                try:
                    self.send(user_id, msg, attachments,
                              forward=forward, destroy=destroy, destroy_type=delete_for_all)
                except vk_api.VkApiError as error:
                    print('{}: {}'.format(user_id, error))
                except ValueError:
                    continue

        broadcast_thread = Thread(target=send_all, args=(message, destroy, destroy_type))
        broadcast_thread.start()
        print("BROADCAST THREAD STARTED")
