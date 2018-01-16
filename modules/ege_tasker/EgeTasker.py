from modules.ege_tasker.interfaces.IEgeTasker import IEgeTasker
from modules.ege_tasker.data_types.Subject import Subject
from modules.ege_tasker.Session import Session
from modules.commands.intefaces.ICommand import ICommand
import mechanicalsoup
import re


class EgeTasker(IEgeTasker, ICommand):

    def __init__(self):
        super().__init__()
        self._triggers= ['ege', 'Ege']
        self._subjects = {}
        self.themes_list = 'There are not theme :('

    def handle(self, command):
        cmd = command.split()
        if cmd[0] not in self._triggers:
            return
        arg = cmd[1:]

        commands = {
            'setup': self.setup,
            'get': '',
        }

        if arg and arg[0] in commands.keys():
            method = commands.get(arg[0])
            arg = arg[1:]
            return method(*arg)
        return 'Bad key'

    def proceed(self, args):
        pass

    def set_group(self, group):
        self._group = group

    def setup(self):
        ege_setuper = Session(self._group)
        ege_setuper.loop()

    def help(self, *args, **kwargs):
        print(args)
        print(kwargs)
        return 'das ist help()'

    def list_subject_themes(self):
        keys = self._subjects.keys()
        result = 'Добавленные предметы:\n'
        for key in keys:
            result += '{}'.format(key)
        return result

    def add_subject(self, name, site):
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(site)
        page = browser.get_current_page()
        points = page.find('table', class_='zebra')
        subject = Subject(name, site)
        for i, point in enumerate(points):
            theme = re.findall('/>([\-\w\s]*) <a href="([/?=\w\s\d]*)"', str(point))
            if theme in [[], None]:
                continue
            subject.configure(theme)
        self._subjects.update({name: subject})
        return subject

    def setup_welcome_message(self):
        text = 'Доброго времени суток.\n'
        text += 'Вы находитесь в программе настройки бота.\n'
        text += 'Команды:\n'
        return text


if __name__ == '__main__':
    ege = EgeTasker()
    subj = ege.add_subject('math', 'https://math-ege.sdamgia.ru')
    subj.setup_themes()
    print(ege.list_subject_themes())
