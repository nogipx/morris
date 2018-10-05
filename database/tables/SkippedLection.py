from peewee import *
from core.settings.db_settings import *

from database.tables.Member import Member


class SkippedLection(Model):

    lid = IntegerField(primary_key=True)
    member_id = ForeignKeyField(Member, on_delete='NO ACTION', unique=True)
    number_lections = IntegerField(default=1)
    skipped_lections = IntegerField(default=0)

    class Meta:
        db_table = "lection"
        database = db