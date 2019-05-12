import vk_api

from vk_communicate.controller.BaseCommunicateVK import BaseCommunicateVK
from vk_communicate.model.User import User
from threading import Thread
from settings import api_version

class Group(BaseCommunicateVK):

    def __init__(self, token, storage=None):
        super().__init__(BaseCommunicateVK.create_session(token, api_version))
        self.members = []
        self.managers = []

    def setup(self):
        self._setup_group()
        self.update_members()
        return self

    def _setup_group(self):
        group = dict(list(self.api.groups.getById())[0])
        self.domain = group.get("screen_name")
        self.group_id = group.get("id")

    def update_members(self):
        fields = 'domain, sex'

        managers = self.api.groups.getMembers(group_id=self.group_id, fields=fields, filter='managers')
        self.save_members(self._configure_users(managers))

        members = self.api.groups.getMembers(group_id=self.group_id, fields=fields)
        self.save_members(self._configure_users(members))

    def save_members(self, members_list):
        upd_users_ids = [user.id for user in members_list]
        cur_count = len(self.members)

        if len(upd_users_ids) != cur_count:
            cur_users_ids = set(self._db.get_members_ids())
            difference = cur_users_ids.symmetric_difference(upd_users_ids)

            if len(cur_users_ids) > len(upd_users_ids):

                for user_id in difference:
                    self._db.delete_member(user_id)

            else:

                for user in members_list:

                    if user.id in difference:
                        self._db.add_member(user)

            self._count = self._db.count()

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

    def get_member_ids(self, managers=False, editors=False, moders=False, sex=0):
        ids = self.storage.get_users_ids(managers=managers, editors=editors, moders=moders, sex=sex)

        return ids

    def get_member(self, uid):
        member = self.storage.get_member(uid)
        user = User()

        for (field, value) in dict(member.__data__).items():
            user.__setattr__(field, value)

        return user

    def broadcast(self, uids, message, attachments=None, destroy=False, destroy_type=0, **kwargs):

        report = BroadcastReport()

        def send_all():
            users_ids = uids
            if not isinstance(users_ids, list):
                users_ids = list(users_ids)

            report.should_be_sent = len(users_ids)


            for user_id in users_ids:
                try:
                    self.send(user_id, message, attachments, destroy=destroy, destroy_type=destroy_type, **kwargs)
                    if message or attachments:
                        report.sent += 1

                except vk_api.VkApiError as error:
                    report.errors.append('vk.com/id{}: {}'.format(user_id, error))

                except ValueError:
                    continue

            for uid in self.get_member_ids(managers=True, moders=True):
                self.send(uid, str(report))

        broadcast_thread = Thread(target=send_all)
        broadcast_thread.start()
        broadcast_thread.join()


class BroadcastReport:

    def __init__(self):
        self.should_be_sent = 0
        self.sent = 0
        self.errors = []

    def __str__(self):
        res = "# Отчет #"
        res += "\nПлан: {} сообщений ".format(self.should_be_sent)
        res += "\nРазослано: {} ".format(self.sent)
        if self.errors:
            res += "\nОшибки:"
            for i in self.errors:
                res += "\n- {}".format(i)
        return res