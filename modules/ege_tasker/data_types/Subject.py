"""
Нужно реализовать систему кеширования отдельных распарсеных записей
Причем так, чтобы получать к ним доступ было как можно легче

Реализовать систему выбора по категориям из чата вк

Сделать возможность применять разные парсеры
То есть вынести парсинг в отдельные класссы
"""
import re
from modules.ege_tasker.data_types.Theme import Theme
import mechanicalsoup


class Subject:

    def __init__(self, name, site):
        self._count = 0
        self._themes = {}
        self.name = name
        self._site = site

    def add_theme(self, theme):
        self._themes.update(theme)
        self._count += 1

    def get_list_themes(self):
        themes = ''
        for i, theme in enumerate(self._themes):
            themes += '{}. {}\n'.format(i, self._themes.get(i).name)
        return themes

    def configure(self, themes):
        self.add_theme(themes)

    def get_theme(self,  theme_num):
        if theme_num in self._themes.keys():
            return self._themes.get(theme_num)
        return "No exist {} theme".format(theme_num)

    def setup_themes(self):
        self._themes.clear()
        self._count = 0
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(self._site)
        page = browser.get_current_page()
        points = page.find('table', class_='zebra')
        title = ''
        links = []

        for i, point in enumerate(points):
            if i not in [0, 1]:
                theme_and_links = re.findall('/>([\-\w\s]*) <a href="([/?=\w\s\d]*)"', str(point))
                if theme_and_links:
                    links.append(theme_and_links)
                point = list(map(str, point))
                if len(point) == 2:
                    title = re.findall('r">([ \w\d\s\S.]*)</a></td>$', str(point[0]))[0].split('. ')[1]
                if links:
                    theme = links.pop(0)
                    for j, block in enumerate(theme):
                        theme_title = theme[j][0]
                        theme_link = theme[j][1]
                        # print('Setting up "{}" for {}'.format(theme_title, title))
                        # print("THEME_LINK: ", theme_link)
                        # print("SUBJ: ", theme_title, theme)
                        # print(self._site + theme_link)
                        # print()
                        theme_obj = Theme(theme_title, self._site + theme_link)
                        self.add_theme({self._count: theme_obj})

    def __str__(self):
        result = '{} - Тем: {}'.format(self.name, len(self._themes))
        return result


if __name__ == '__main__':
    sub = Subject('math', 'http://math-ege.sdamgia.ru')
    sub.setup_themes()
    print(sub.get_list_themes())
    theme4 = sub.get_theme(4)
    theme4.setup_problems()
    problem = theme4.get_problem(6)
    print(problem.get_text())

    # sub.get_list_themes()


