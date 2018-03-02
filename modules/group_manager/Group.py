import vk_api
import logging

from modules.group_manager.data_types.User import User
from modules.group_manager.IGroup import IGroup


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

    def delete(self, msg_id):
        self._vk.method('messages.delete', {
            'message_id': msg_id,
            'delete_for_all': 1})

    def send(self, user_id, message, attachments):
        print('SEND', user_id, message, attachments)
        send_to = int(user_id)

        self._vk.method('messages.send', {
            'user_id': send_to,
            'message': message,
            'attachment': self._parse_attachments(attachments)
        })

    def broadcast(self, users_ids, message, attachments, sender_id=0):
        if not message:
            return

        for user_id in users_ids:
            try:
                if user_id == sender_id:
                    message = 'Sended'
                self._vk.method("messages.send", {
                    'user_id': user_id,
                    "message": message,
                    "attachments": self._parse_attachments(attachments)
                })
            except vk_api.VkApiError as error:
                print('{}: {}'.format(user_id, error))
            except ValueError:
                continue

    @staticmethod
    def _parse_attachments(attachments):
        attach = []
        result = ''
        files = attachments
        amount = 0

        if attachments is None:
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
