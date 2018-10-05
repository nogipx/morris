import vk_api

from vk_communicate.controller.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.model.User import User
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
        self.save_members(self._configure_users(admins))

        members = self.api.groups.getMembers(group_id=self.group_id, fields=fields)
        self.save_members(self._configure_users(members))

        return self

    def save_members(self, members):
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

    def get_member_ids(self, admins=False, editors=False, moders=False, sex=0):
        ids = self.storage.get_users_ids(admins=admins, editors=editors, moders=moders, sex=sex)

        return ids

    def get_member(self, uid):
        member = self.storage.get_member(uid)
        user = User()

        for (field, value) in dict(member.__data__).items():
            user.__setattr__(field, value)

        return user

    def broadcast(self, users_ids, message, attachments=None, destroy=False, destroy_type=0):

        def send_all():
            for user_id in users_ids:
                try:
                    self.send(user_id, message, attachments, destroy=destroy, destroy_type=destroy_type)
                except vk_api.VkApiError as error:
                    print('{}: {}'.format(user_id, error))
                except ValueError:
                    continue

        broadcast_thread = Thread(target=send_all)
        broadcast_thread.start()
        broadcast_thread.join()
        print("BROADCAST THREAD STARTED")
