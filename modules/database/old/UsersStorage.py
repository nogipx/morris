
class UsersStorage:

    __instance__ = None

    def __init__(self):
        self.admins_ids = []
        self._users_ids = []
        self._users = []

    @staticmethod
    def get_storage():
        if UsersStorage.__instance__ is None:
            UsersStorage.__instance__ = UsersStorage()
        return UsersStorage.__instance__

    def get_users(self, admins=False):
        if admins:
            return [self.find_user(user_id) for user_id in self.admins_ids]
        return self._users

    def find_user(self, user_id):
        for user in self._users:
            if user.id == user_id:
                return user

    def add_user(self, user):
        if user.id not in self._users_ids:
            if user.role:
                self.admins_ids.append(user.id)
            self._users.append(user)
            self._users_ids.append(user.id)
