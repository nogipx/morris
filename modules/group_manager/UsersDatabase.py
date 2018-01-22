import sqlite3

class UsersDatabase:

    __instance__ = None

    @staticmethod
    def get_storage():
        if UsersDatabase.__instance__ is None:
            UsersDatabase.__instance__ = UsersDatabase()
        return UsersDatabase.__instance__
