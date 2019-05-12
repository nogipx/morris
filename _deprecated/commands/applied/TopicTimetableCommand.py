from commands.core.Command import Command
import datetime


class TopicTimetableCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.t', '.T', '.tt', '.Tt']
        self._short_tt = ['.t', '.T']
        self._full_tt = ['.tt', '.Tt']
        self.days = []
        self.account = None
        self.group_id = None

    def proceed(self, member, message, attachments, group, **kwargs):
        self.group_id = group.group_id
        try:
            self.update()
        except Exception:
            message = "Сейчас не удаётся отправить расписание. \nВозможно не создано обсуждение с расписанием."
            group.send(member.id, message, attachments)
            return

        trigger = kwargs["trigger"]

        status = True

        if trigger in self._short_tt:
            status = group.send(member.id, self.get_short_timetable(), attachments)

        elif trigger in self._full_tt:
            status = group.send(member.id, self.get_full_timetable(), attachments)

        if status is False:
            message = "Сейчас не удаётся отправить расписание. \nПопробуйте позже."
            group.send(member.id, message, attachments)

        return True

    def setup_account(self, account):
        self.account = account
        return self

    def update(self):
        if self.account is None:
            raise ValueError('BotAccount is not defined')

        self.parse_all_week(self.find_timetable_topic_id(self.group_id))


    def find_timetable_topic_id(self, group_id):
        topics = self.account.board.getTopics(
            group_id=group_id,
            preview=1,
            preview_length=0,
            order=2)

        items = topics.get('items')
        timetable_title = ['Расписание', 'Timetable']
        for topic in items:
            if topic.get('title') in timetable_title:
                return topic.get('id')

    def parse_all_week(self, topic_id):
        self.days = []
        comments = self.account.board.getComments(
            group_id=self.group_id,
            topic_id=topic_id,
            count=6)

        for comment in comments.get('items'):
            text = comment.get('text')
            self.days.append(text)

    def get_full_timetable(self):
        timetable = ''
        for day in self.days:
            timetable += day + '\n' * 2
        return timetable

    def get_short_timetable(self):
        today = datetime.datetime.today().timetuple()
        wday = today.tm_wday
        if today.tm_hour < 13:
            return self.days[wday]
        else:
            return self.days[self.inc_day(wday)]

    def inc_day(self, today):
        if today in [5, 6]:
            return 0
        return today+1
