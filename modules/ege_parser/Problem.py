class Problem:
    def __init__(self, theme, prob_id, text, help, solve, images):
        self.theme_name = theme
        self.problem_id = prob_id
        self.text = text
        self.help = help
        self.solve = solve
        self.images = images

    def join(self, part1, part2):
        pattern = '{}.{}'
        return pattern.format(part1, part2)

    def __str__(self):
        res = '='*20 + '\n'
        for key in self.__dict__:
            res += '{} - {}\n'.format(key, self.__dict__.get(key))
        res += '='*20 + '\n'
        return res
