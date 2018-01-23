from abc import ABCMeta, abstractmethod


class ICommand(metaclass=ABCMeta):

    def __init__(self):
        self._triggers = []
        self.activate_times = []
        self.activate_days = set()

    @abstractmethod
    def proceed(self, *args):
        """
        :param args:
        - First arg always is 'user_id'
        - Second arg is 'command'
        - Other args are internal params for command
        :return:
        """
        pass

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
            if day > 7:
                day = 7
            elif day < 0:
                day = 0
            self.activate_days.add(day)

    def handle(self, user_id, message):
        cmd = message.split()
        for key in cmd:
            if key in self._triggers:
                func = cmd[0]
                func_args = cmd[1:]
                return self.proceed(user_id, func, *func_args)
        return None

    def generate_name(self):
        self.name = self._triggers[0]