from modules.commands.intefaces.ICommand import ICommand
from BotAccount import BotAccount
import datetime


class TopicTimetableCommand(ICommand):

    def __init__(self, group_id, account):
        super().__init__()
        self._triggers = ['t', 'T']
        self._extra_triggers = ['tt', 'Tt']
        self._days = []
        self._account = account
        self._group_id = group_id
        self.update()

    def proceed(self, args):
        if self._days:
            tt = ''
            for day in self._days:
                tt += day + '\n'*2
            if 't' in args:
                return self.get_tomorrow()
            return tt

    def handle(self, command):
        cmd = command.split()
        args = cmd[1:]
        if cmd[0] in self._triggers:
            return self.get_tomorrow()
        if cmd[0] in self._extra_triggers:
            return self.proceed(args)

    def setup_bot_account(self, account):
        self._account = account

    def update(self):
        if self._account is None:
            raise ValueError('BotAccount does not defined')
        self.parse_all_week(self.find_timetable_topic_id(self._group_id))

    def find_timetable_topic_id(self, group_id):
        topics = self._account.method('board.getTopics', {
            'group_id': group_id,
            'preview': 1,
            'preview_length': 0,
            'order': 2
        })
        items = topics.get('items')
        timetable_title = ['Расписание', 'Timetable']
        for topic in items:
            if topic.get('title') in timetable_title:
                return topic.get('id')

    def parse_all_week(self, topic_id):
        self._days = []
        comments = self._account.method('board.getComments', {
            'group_id': self._group_id,
            'topic_id': topic_id,
            'count': 6
        })
        for comment in comments.get('items'):
            text = comment.get('text')
            self._days.append(text)

    def get_tomorrow(self):
        today = datetime.datetime.today().timetuple().tm_wday
        return self._days[self.inc_day(today)]

    def inc_day(self, today):
        if today in [5, 6]:
            return 0
        return today+1
