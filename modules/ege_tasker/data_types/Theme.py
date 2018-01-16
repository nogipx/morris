import mechanicalsoup

from modules.ege_tasker.data_types.Problem import Problem


class Theme:

    def __init__(self, name, site):
        self._site = site
        self.name = name
        self._problems = {}
        self._count = 1

    def get_problems(self):
        return self._problems

    def add_problem(self, problem):
        self._problems.update(problem)
        self._count += 1

    def setup_problems(self):
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(self._site)
        maths = browser.get_current_page().find_all('div', class_='prob_view')
        for math in maths:
            problem = Problem(math)
            problem.configure()
            self.add_problem({self._count: problem})

    def get_problem(self, problem_num):
        if problem_num in self._problems.keys():
            return self._problems.get(problem_num)
        return "No exist {} problem".format(problem_num)

    def __str__(self):
        result = '=' * 20 + '\n'
        ids = []
        count = 0
        for problem in self._problems:
            count = len(self._problems)
            ids.append(problem.prob_id)
        result += 'Тема: {theme}\n'\
                  'Кол-во заданий: {count}\n' \
                  'ID заданий: {ids}\n'.format(
            theme=self.name,
            count=count,
            ids=ids
        )
        result += '=' * 20 + '\n'
        return result
