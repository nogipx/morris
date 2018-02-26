from peewee import *
from modules.group_manager.data_types.User import User
import peewee
from threading import Thread

db = SqliteDatabase('NEW_ORM_DB.db')


class Member(Model):
    uid = IntegerField(primary_key=True, index=True, unique=True)
    domain = CharField()
    first_name = CharField()
    last_name = CharField()
    role = CharField(null=True)

    class Meta:
        db_table = "Member"
        database = db

    @staticmethod
    def get_user(user_id):
        user = Member.select().where(Member.uid == user_id).get()
        return user

    @staticmethod
    def add_user(member):
        args = {}
        for key in member.__dict__:
            args.update({key: member.__dict__.get(key)})
        try:
            Member.create(**args)
        except IntegrityError as error:
            print('Error with insert: uid={}, domain="{}" already exists.'.format(member.uid, member.domain))

    def get_commands(self):
        commands = Command.select().where(Command.user_id == self.uid)
        return commands


class Command(Model):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(Member)
    name = CharField()
    times = CharField(null=True)
    days = CharField(null=True)

    class Meta:
        db_table = 'Command'
        database = db   


__models__ = [Member, Command]
