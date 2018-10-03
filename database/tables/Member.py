from peewee import *
from database.db_settings import *


class Member(Model):
    id = IntegerField(primary_key=True, index=True, unique=True)
    domain = CharField()
    first_name = CharField()
    last_name = CharField()
    role = CharField(null=True)
    sex = IntegerField()

    class Meta:
        db_table = "member"
        database = db