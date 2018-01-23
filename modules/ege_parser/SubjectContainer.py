import mechanicalsoup
import re
from bs4.element import NavigableString, Tag, ResultSet


class SubjectParser:

    def __init__(self, subject_name, site):
        self.subject_name = subject_name
        self._site = site
        self.tasks = {}
        self.themes = {}

    def parse_site_for_tasks(self):
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(self._site)
        page = browser.get_current_page()
        html_tables = page.select('table')[1].select('> tr')[1:]
        html_tables.pop()

        tasks = []
        html_tables.reverse()
        for i in range(len(html_tables)//2):
            tasks.append([html_tables.pop(), html_tables.pop()])

        html_tables = tasks

        for html_task in html_tables:
            task_name = html_task[0].find('a').text
            task_themes = html_task[1].findAll('td',  style="padding-left:10px")
            themes = self.setup_themes(task_themes)
            print('\nNEW TASK YEAH\n\n')
        return None

    def setup_tasks(self):
        pass

    def setup_themes(self, html_block):
        themes = []
        # print(len(html_block))
        while html_block:
            tag = html_block.pop()
            # print(tag.prettify())
            theme_name = tag.getText().rstrip('просмотреть')
            if theme_name:
                theme_link = tag.find('a', style="font-size:8pt").get('href')
                # print(theme_name, theme_link)
        return themes


if __name__ == '__main__':
    subj = SubjectParser('math', 'http://math-ege.sdamgia.ru')
    subj.parse_site_for_tasks()
