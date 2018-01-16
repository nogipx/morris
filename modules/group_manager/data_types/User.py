class User:
    def __init__(self):
        self.first_name = ""
        self.last_name = ""
        self.id = ""
        self.domain = ""
        self.personal = ""
        self.lists = []

    def add_to_list(self, lists):
        self.lists.append(lists)

    def get_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_info(self):
        return self

    def configure(self, **kwargs):
        for arg in kwargs:
            if not self.__dict__.get(arg):
                self.__setattr__(arg, kwargs.get(arg))

    def parse_configure(self, config):
        config = config.strip('[]{}').split(',')
        conf = {}
        for setting in config:
            setting = setting.split(':')
            key = setting[0].strip('{}{}{}'.format("'", '"', ' '))
            value = setting[1].strip('{}{}{}'.format("'", '"', ' '))
            conf.update({key: value})
        self.configure(**conf)

    def __str__(self):
        user = '-' * 20 + '\n'
        for key in self.__dict__:
            user += '{} = {}'.format(key, self.__dict__.get(key))
            user += '\n'
        user += '-' * 20 + '\n'
        return user

