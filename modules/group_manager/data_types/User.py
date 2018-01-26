class User:
    def __init__(self, **kwargs):
        for key in kwargs:
            self.__setattr__(key, kwargs.get(key))
        self.session_thread = None

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

if __name__ == '__main__':
    import vk_api
    token = '7134ec6b881f83f140dcbdd6a0e0e3001300a2b9f69bc5d13341d0bf650797564141ed907b2dcf8df1e93'
    group = vk_api.VkApi(token=token)
    print(group.method('groups.getMembers', {
        'group_id': 'test11aof',
        'fields': 'domain, role'
    }))
