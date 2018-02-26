from peewee import *

name_db = 'UsersDatabase.db'


def database_name(name):
    global name_db
    name_db = name


db = SqliteDatabase(name_db)


class Member(Model):
    id = IntegerField(primary_key=True, index=True, unique=True)
    domain = CharField()
    first_name = CharField()
    last_name = CharField()
    role = CharField(null=True)

    class Meta:
        db_table = "Member"
        database = db

    @staticmethod
    def init_db():
        db.create_tables(__models__, safe=True)

    @staticmethod
    def count():
        return len(Member.get_members_ids())

    @staticmethod
    def add_member(member):
        try:
            Member.create(**member.__dict__)
        except IntegrityError as error:
            print('INSERT FAILED: id={}, domain="{}" already exists.'
                  .format(member.id, member.domain))

    @staticmethod
    def delete_member(user_id):
        delete = Member.delete().where(Member.id == user_id)
        delete.execute()

    @staticmethod
    def get_member(user_id, *args):
        user = Member.select(*args).where(Member.id == user_id).get()
        return user

    @staticmethod
    def get_members_ids(admins=False, editors=False, moders=False):
        if admins:
            query = Member.select().where(
                (Member.role == 'administrator') |
                (Member.role == 'creator'))
        elif editors:
            query = Member.select().where(
                Member.role == 'editor')
        elif moders:
            query = Member.select().where(
                Member.role == 'moderator')
        else:
            query = Member.select()
        return [user.id for user in query]

    def get_commands(self):
        commands = Command.select().where(Command.user_id == self.id)
        return commands

    def add_command(self, name, days, times):
        Command.create(user_id_id=self.id, name=name, days=days, times=times)

    def remove_command(self, name):
        commands = Command.delete().where(Command.user_id == self.id, Command.name == name)
        commands.execute()


class Command(Model):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(Member, on_delete='NO ACTION')
    name = CharField()
    times = CharField(null=True)
    days = CharField(null=True)

    class Meta:
        db_table = 'Command'
        database = db


__models__ = [Member, Command]
