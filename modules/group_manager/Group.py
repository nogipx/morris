import vk_api
import logging

from modules.group_manager.data_types.User import User
from modules.group_manager.IGroup import IGroup
from threading import Thread


class Group(IGroup):

    def auth(self, token):
        try:
            self._vk = vk_api.VkApi(token=token)
        except vk_api.ApiError as error:
            logging.info(error)

    def set_exclude_ids(self, exclude):
        self._exclude = exclude

    def connect_storage(self, storage):
        self._storage = storage
        self.setup()

    def setup(self):
        self._setup_group()
        self.update_members()

    def _setup_group(self):
        group = dict(list(self._vk.method('groups.getById'))[0])
        self._group_domain = group.get("screen_name")
        self.group_id = group.get("id")

    def update_members(self):
        fields = 'domain, sex'

        def api_get_members(vk, **kwargs):
            return vk.method('groups.getMembers', kwargs)

        admins = api_get_members(self._vk, group_id=self.group_id, fields=fields, filter='managers')
        self._put_into_storage(self._configure_users(admins))

        members = api_get_members(self._vk, group_id=self.group_id, fields=fields)
        self._put_into_storage(self._configure_users(members))

    def _put_into_storage(self, members):
        self._storage.update(members)

    # Было бы лучше, если бы пользователи добавлялись напрямую в бд, а не через дополнительный класс
    @staticmethod
    def _configure_users(items, exclude=list()):
        users = []
        for user in items.get('items'):
            if user.get('id') not in exclude:
                member = User()
                member.configure(**user)
                users.append(member)
        return users

    def get_member_ids(self, admins=False, sex=0):
        ids = self._storage.get_users_ids(admins=admins, sex=sex)
        return ids

    def get_member(self, uid):
        member = self._storage.get_member(uid)
        print(member.id, member.domain)
        user = User()
        for field in member._data:
            user.__setattr__(field, member._data.get(field))
        print(user)
        return user

    def delete(self, msg_id, destroy_type=1):
        self._vk.method('messages.delete', {
            'message_id': msg_id,
            'delete_for_all': destroy_type})

    def send(self, user_id, message, attachments=None, forward=None, destroy=False, destroy_type=0):
        # print('SEND', user_id, message, attachments)
        send_to = int(user_id)
        if message or attachments:
            self._vk.method('messages.send', {
                'user_id': send_to,
                'message': message,
                'attachment': self._parse_attachments(attachments),
                'forward_messages': forward})

        else:
            raise vk_api.VkApiError('There are not message and attachment.')

        if destroy:
            accept_msg_id = self._vk.method('messages.getHistory', {
                'peer_id': user_id,
                'count': 1
            }).get('items')[0].get('id')
            self.delete(accept_msg_id, destroy_type=destroy_type)

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

    @staticmethod
    def _parse_attachments(attachments):
        attach = []
        result = ''
        files = attachments
        amount = 0

        if not attachments:
            return

        for file in files.keys():
            if str(file).endswith('type'):
                amount += 1
                attach.append((files.get('attach{0}_type'.format(amount)) + files.get('attach{0}'.format(amount))))
        for i in attach:
            result += '{},'.format(i)
        return result

    def get_api(self):
        return self._vk

    def method(self, func, args):
        return self._vk.method(func, args)
