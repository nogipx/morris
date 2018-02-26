import re
import datetime
from modules.commands.interface.ICommand import ICommand


class Note:
    def __init__(self):
        self.name = ''
        self.dz = ''
        self.date = datetime.datetime.today()

    def __str__(self):
        tt = self.date.timetuple()
        weekday = self.weekday(self.get_calendar()[2])
        return '\n{} \n# {}\n@ {}'.format(self.name.upper(),
                                          '{}, {}'.format(weekday, '{} {}'.format(tt.tm_mday, self.month(tt.tm_mon))),
                                          self.dz)

    @staticmethod
    def month(month):
        return {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"
        }.get(month)

    @staticmethod
    def weekday(wday):
        return {
            0: "Воскресенье",
            1: "Понедельник",
            2: "Вторник",
            3: "Среда",
            4: "Четверг",
            5: "Пятница",
            6: "Суббота",
        }.get(wday)

    def get_calendar(self):
        return self.date.isocalendar()


class HomeworkCommand(ICommand):

    def __init__(self, bot_account, group_id):
        super().__init__()
        self._triggers = ['hw', 'Hw']
        self.account = bot_account
        self.group_id = group_id
        self.recent_notes = []
        self.last_id = 0

    def proceed(self, *args, **kwargs):
        if len(args) > 0 and args[1] in self._triggers:
            return self.week()
        return False

    def sort(self, result):
        return sorted(result, key=self.sortByDate)

    @staticmethod
    def sortByDate(note):
        return note.date.timetuple().tm_yday

    @staticmethod
    def parse_lessons(text):
        calendar = '📅'
        books = '📚'
        name_sep = '#'
        lessons = text.rsplit('_')
        notes = []

        for lesson in lessons:
            note = Note()
            try:
                note.name = re.search(name_sep + " ?[А-я ]*", lesson).group().strip("# \n")

                date = re.search(calendar + " ?[^`]*{}".format(books), lesson).group().strip("{}{} \n".format(calendar, books))
                date = '{}.{}'.format(date, datetime.datetime.today().timetuple().tm_year)
                date = datetime.datetime.strptime(date, '%d.%m.%Y').date()
                note.date = date

                note.dz = re.search(books + " ?[^`]*\n?", lesson).group().strip("{} \n".format(books))

                notes.append(note)
            except:
                continue

        return notes

    def update_posts(self,account, group_id, count):
        if group_id > 0:
            group_id *= -1
        print(account)
        posts = account.method('wall.get', {
            'owner_id': group_id,
            'count': count,
            'fields': 'domain, lists',
            'filter': 'all'
        })
        posts = posts.get('items')
        recent_notes = []

        for post in posts:
            text = post.get('text')
            if re.sub('^#ДЗ *\n?$', '', text) or re.sub('^#дз *\n?$', '', text):
                lessons = self.parse_lessons(text.lstrip('#дзДЗ'))
                for note in lessons:
                    if note is not None:
                        recent_notes.append(note)

        return recent_notes

    def get_this_week(self, count):
        today = datetime.datetime.today()
        td = today.isocalendar()
        td_year, td_week, td_wday = td[0], td[1], td[2]
        result = []

        for note in self.update_posts(self.account, self.group_id, count):
            note_calendar = note.get_calendar()
            nt_year, nt_week, nt_wday = note_calendar[0], note_calendar[1], note_calendar[2]
            if nt_week == td_week and nt_wday >= td_wday:
                if td_wday not in [6, 7]:
                    td_tt = today.timetuple()
                    if td_wday == nt_wday and td_tt.tm_hour >= 13:
                        continue
                    result.append(note)
                elif nt_week == td_week + 1:
                    result.append(note)

        return self.sort(result)

    def week(self):
        result = '{}'.format('-' * 0)
        for note in self.get_this_week(50):
            result += '{}\n{}'.format(str(note), '-' * 20)
        if result is '':
            result = 'Записей нет.'
        return result
