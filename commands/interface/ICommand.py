from abc import ABCMeta, abstractmethod


class ICommand(metaclass=ABCMeta):

    def __init__(self):
        self.triggers = []
        self.activate_times = []
        self.activate_days = set()
        self.autostart_func = self.proceed

    @abstractmethod
    def proceed(self, *args, **kwargs):
        """
        :param args:
        - First arg always is 'user_id'
        - Second arg is 'command'
        - Other args are internal params for command
        :return:
        """
        raise NotImplementedError()

    def clear(self, *args):
        if 'times' in args:
            self.activate_times.clear()
        if 'days' in args:
            self.activate_days.clear()

    def add_activate_time(self, *times):
        for time in times:
            self.activate_times.append(time)

    def add_activate_wday(self, *days, **kwargs):
        for key in kwargs:
            value = kwargs.get(key)
            if key == 'all_week' and value is True:
                for day in range(1, 7):
                    self.activate_days.add(day)
            return

        for day in days:
            if day > 6:
                day = 6
            elif day < 0:
                day = 0
            self.activate_days.add(day)

    def handle(self, user_id, message, **kwargs):
        for part in message:
            if part in self.triggers:
                func = part
                func_args = message[1:]
                return self.proceed(user_id, func, *func_args, **kwargs)
        return None

    def generate_name(self):
        self.name = self.triggers[0]