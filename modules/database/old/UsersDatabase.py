import os
import sqlite3
from modules.group_manager.data_types.User import User


class UsersDatabase:
    __instance__ = None

    def __init__(self, db_name):
        self._connection = sqlite3.connect(db_name)
        self._count = 0

    # def conn(self, db_name):
    #     self._connection = sqlite3.connect(db_name)
    #     return self

    @staticmethod
    def get_storage(*args):
        if UsersDatabase.__instance__ is None:
            UsersDatabase.__instance__ = UsersDatabase(*args)
        return UsersDatabase.__instance__

    def init_db(self):
        cursor = self._connection.cursor()
        init_script = os.path.join(os.getcwd(), 'data_types', 'db_init.sql')
        if os.path.exists(init_script):
            pass

        init_script = \
            """
            PRAGMA foreign_keys = off;
            BEGIN TRANSACTION;
            
            CREATE TABLE IF NOT EXISTS User (
                id         INTEGER PRIMARY KEY
                                   NOT NULL,
                domain,
                first_name STRING,
                last_name  STRING,
                role       STRING
            );
            
            CREATE TABLE IF NOT EXISTS Config (
                user_id INTEGER REFERENCES User (id) ON DELETE CASCADE
                                                     ON UPDATE CASCADE
                                NOT NULL
                                UNIQUE,
                id      INTEGER PRIMARY KEY AUTOINCREMENT
                                NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Command (
                config_id INTEGER REFERENCES Config (id) ON DELETE CASCADE,
                name      STRING,
                time      STRING,
                days      INTEGER
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS MemberInfo ON User (
                id,
                domain,
                first_name,
                last_name
            );
            
            COMMIT TRANSACTION;
            PRAGMA foreign_keys = on;
            """
        cursor.executescript(init_script)
        return self

    def execute(self, sql):
        cursor = self._connection.cursor()
        try:
            cursor.execute(sql)
        except sqlite3.ProgrammingError as error:
            print(error)
        print('WARNING! Danger construction have been passed...')
        return cursor

    def count(self):
        sql = """ SELECT id FROM User; """
        res = self.execute(sql)
        return len(res.fetchall())

    def add_user(self, user):
        sql_command = 'INSERT OR IGNORE INTO'
        sql = \
            """
            {cmd} User (id, domain, first_name, last_name, role) 
            VALUES ({user_id}, '{domain}', '{first_name}', '{last_name}', '{role}')
            """.format(
                cmd=sql_command,
                user_id=user.id,
                domain=user.domain,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role
            )
        self.execute(sql)
        self._connection.commit()

    def get_user(self, user_id):
        user = User()
        sql = \
            """
            SELECT User.*
            FROM User
            WHERE User.id == {user_id}
            """.format(user_id=user_id)
        res = self.execute(sql)
        info = res.fetchone()
        user.id = info[0]
        user.domain = info[1]
        user.first_name = info[2]
        user.last_name = info[3]
        user.role = [4]
        return user

    def get_commands_for_user(self, user_id):
        sql = \
            """
            SELECT User.domain, Command.name, Command.time, Command.days
            FROM User, Config, Command
            WHERE 
                User.id == {user_id} AND
                Config.user_id == User.id AND
                Command.config_id == Config.id
            """.format(user_id=user_id)
        res = self.execute(sql)
        return res.fetchall()

    def get_ids_command(self, command):
        sql = \
            """
            SELECT DISTINCT User.id
            FROM User, Config, Command
            WHERE 
                Config.user_id == User.id AND
                Command.config_id == Config.id AND
                Command.name = '{command}'
            """.format(command=command)
        res = self.execute(sql)
        users = res.fetchall()
        return users

    def get_users_ids(self, admins=False, editors=False, moders=False):
        role = 'User.role == "{}" OR '
        where = ''
        if admins:
            where += role.format('creator')
            where += role.format('administrator')
        if editors:
            where += role.format('editor')
        if moders:
            where += role.format('moder')
        where = where.rstrip(' OR')

        sql = \
            """
            SELECT id
            FROM User
            {WHERE}
            """.format(WHERE='WHERE {}'.format(where) if where else '')

        res = self.execute(sql)
        ids = res.fetchall()
        return [uid[0] for uid in ids]

    def delete_user(self, user_id):
        sql = \
            """DELETE FROM User WHERE User.id == {uid}""".format(uid=user_id)
        self.execute(sql)
        self._connection.commit()

    def update_user(self, user):
        sql = \
            """
            UPDATE User
                SET id = {id},
                    domain = '{domain}',
                    first_name = '{first_name}',
                    last_name = '{last_name}',
                    role = '{role}'
            WHERE id = '{id}' AND domain = '{domain}'
            """.format(
                id=user.id,
                domain=user.domain,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role
            )
        self.execute(sql)
        self._connection.commit()

    def update(self, upd_users):
        upd_users_ids = [user.id for user in upd_users]
        cur_count = self.count()
        if len(upd_users_ids) != cur_count:
            cur_users_ids = set(self.get_users_ids())
            difference = cur_users_ids.symmetric_difference(upd_users_ids)
            if len(cur_users_ids) > len(upd_users_ids):
                for user_id in difference:
                    self.delete_user(user_id)
            else:
                for user in upd_users:
                    if user.id in difference:
                        self.add_user(user)
            self._count = self.count()


if __name__ == '__main__':
    db = UsersDatabase.get_storage().conn('TestUserDB.db').init_db()
    user = db.get_user(1)
    user.role = 'editor'
    db.update_user(user)
    # print('GETTING USER ID=2')
    # print(db.get_user(1))
    # print()
    # print('GETTING ALL USERS IDS')
    # print(db.get_users_ids(admins=True))
    # print()
    # print('GETTING COMMAND IDS')
    # print(db.user_with_command('me'))
