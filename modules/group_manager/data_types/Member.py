class Member:

    def __init__(self):
        self.info = {
            'first_name': '',
            'last_name': '',
            'id': '',
            'domain': '',
            'personal': ''
        }
        self.lists = []

    def configure(self, **kwargs):
        for key in kwargs:
            if key in self.info.keys():
                self.info.update({key: kwargs.get(key)})

    def add_to_list(self, lists):
        self.lists.append(lists)

    def get_name(self):
        return self.info.get('first_name') + self.info.get('last_name')

    def get_info(self):
        return dict(self.info)

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
        for key in self.info.keys():
            user += '{} = {}'.format(key, self.info.get(key))
            user += '\n'
        user += '-' * 20 + '\n'
        return user
