from database.StorageInterface import StorageInterface


class DBProxy(StorageInterface):

    def __init__(self, db_class):
        self._db = db_class
        self._db.init_db()

    def update(self, update_users):
        upd_users_ids = [user.id for user in update_users]
        cur_count = self._db.count()

        if len(upd_users_ids) != cur_count:
            cur_users_ids = set(self._db.get_members_ids())
            difference = cur_users_ids.symmetric_difference(upd_users_ids)

            if len(cur_users_ids) > len(upd_users_ids):

                for user_id in difference:
                    self._db.delete_member(user_id)

            else:

                for user in update_users:

                    if user.id in difference:
                        self._db.add_member(user)

            self._count = self._db.count()

    def get_users_ids(self, **kwargs):
        return self._db.get_members_ids(**kwargs)

    def get_member(self, uid):
        try:
            return self._db.get_member(uid)
        except Exception:
            self.update([uid, ])
            return self._db.get_member(uid)

    def skipped_percents(self, uid):
        return self._db.skipped_percents(uid)

    def get_skipped(self, uid):
        return self._db.get_skipped(uid)

    def increase_skipped(self, uid, value):
        self._db.increase_skipped(uid, value)

    def decrease_skipped(self, uid, value):
        self._db.decrease_skipped(uid, value)


if __name__ == '__main__':
    db = DBProxy()
    db.update()
    print(db.get_users_ids())