import re, json
from abc import ABCMeta


class Command(metaclass=ABCMeta):

    def __init__(self, trigger):
        self.trigger = trigger
        self.description = "Empty description."

        self.system = False
        self.privilege = False
        self.keyboard = { 
            "action": { 
                "type": "text", 
                "payload": json.dumps({'button': self.trigger}), 
                "label": "Empty"
            }, 
            "color": "default" 
        }

        self.activate_times = []
        self.activate_days = set()
        self.autostart = self.proceed

    def proceed(self, member, message, attachments, group, **kwargs):
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

    def name(self):
        return "{} - {}".format(self.trigger, self.description)

    @staticmethod
    def get_body(kw, message):
        if not isinstance(kw, list): kw = [kw, ]

        for i in kw:
            reg = '^ *(\\{}) *'.format(i)

            if re.search(reg, message):
                return re.sub(reg, '', message).strip(' ')
