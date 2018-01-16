import mechanicalsoup
from modules.commands.intefaces.ICommand import ICommand


class Problem:

    def __init__(self, problem):
        super().__init__()
        self.problem = problem

    def configure(self):
        self.setup_id()
        self.setup_prob_text()
        self.setup_help()

    def get_text(self):
        return self.text

    def get_help(self):
        return self.help

    def get_id(self):
        return self.prob_id

    def setup_id(self):
        prob = self.problem.find('span', class_='prob_nums')
        self.prob_id = str(prob.a.text).strip()

    def setup_prob_text(self):
        tag = 'body' + self.prob_id
        text = self.problem.find('div', class_='pbody')
        paragraphs = text.select('p')
        self.text = ''
        for paragraph in paragraphs:
            self.text += '{}\n'.format(str(paragraph.text).strip())

    def setup_help(self):
        tag = 'sol' + self.prob_id
        text = self.problem.find('div', id=tag)
        helps = text.select('p')
        self.help = ''
        for help in helps:
            self.help += '{}\n'.format(str(help.text).strip())

    def __str__(self):
        desc = '-'*20 + '\n'
        for attr in self.__dict__:
            if attr is 'problem':
                continue
            desc += '{} = {}\n'.format(attr, self.__dict__.get(attr))
        desc += '-'*20
        return desc

if __name__ == '__main__':
    pass

