from peewee import *
from core.settings.db_settings import *

from database.tables.Member import Member
from database.tables.SkippedLection import SkippedLection

__models__ = [Member, SkippedLection]

# Вполне возможны ошибки выполнения, т.к. бд работает синхронно
# Причина: разные треды для каждого пользователя
# Решение: перевод бд в асинхронный режим


def database_name(name):
    global name_db
    name_db = name


def init_db():
    db.create_tables(__models__, safe=True)

########################################################################################################################
### Member ###


def count():
    return len(get_members_ids())


def add_member(member):
    try:
        Member.create(**member.__dict__)
    except IntegrityError:
        print('INSERT FAILED: id={}, domain="{}" already exists.'
              .format(member.id, member.domain))


def delete_member(user_id):
    Member.delete().where(Member.id == user_id).execute()


def get_member(user_id, *args):
    return Member.select(*args).where(Member.id == user_id).get()


# 2 - Male
# 1 - Female
# 0 - All

def get_members_ids(admins=False, editors=False, moders=False, sex=0):
    query = Member.select()
    if sex == 0:
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
    elif sex == 1:
        query = Member.select().where(
            Member.sex == sex)
    elif sex == 2:
        query = Member.select().where(
            Member.sex == sex)
    return [user.id for user in query]

########################################################################################################################
### Skipped lections ###


def skipped_percents(uid):
    info = SkippedLection.get_or_create(member_id_id=uid)[0]
    return info.skipped_lections / info.number_lections * 100


def get_skipped(uid):
    return SkippedLection.get_or_create(member_id=uid)[0].skipped_lections


def increase_skipped(uid, value):
    SkippedLection\
        .update(skipped_lections=SkippedLection.skipped_lections + value)\
        .where(SkippedLection.member_id == uid).execute()


def decrease_skipped(uid, value):
    cur_scipped = get_skipped(uid)
    if cur_scipped - int(value) < 0:
        value = cur_scipped
    SkippedLection\
        .update(skipped_lections=SkippedLection.skipped_lections - value)\
        .where(SkippedLection.member_id == uid).execute()
