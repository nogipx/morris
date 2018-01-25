from modules.interfaces.IObserver import IObserver
from collections import deque
import datetime
import time


class NotifyCheckerObserver(IObserver):

    __instance__ = None

    def __init__(self):
        super().__init__()
        self._msg_queue = deque()

    def set_group(self, group):
        self._group = group

    def execute(self, *args):

        def first_zero(some_time):
            if len(str(some_time)) == 1:
                some_time = '0' + str(some_time)
                return some_time
            return some_time

        start_min = 0
        while True:
            today = datetime.datetime.today().timetuple()
            minute = today.tm_min
            if start_min != minute:
                start_min = minute
            else:
                time.sleep(40)
                continue

            wday = today.tm_wday
            hour = today.tm_hour
            ctime = '{hour}:{minute}'.format(
                hour=hour,
                minute=first_zero(minute))

            for command in self._commands:
                print(command.name, command.activate_times, command.activate_days)
                if wday in command.activate_days and \
                        ctime in command.activate_times:
                    self._msg_queue.append(command.proceed(*args))

            while len(self._msg_queue) > 0:
                message = self._msg_queue.popleft()
                if message:
                    self._group.broadcast(self._group.get_members(), message, None)



if __name__ == '__main__':
    from modules.notify_checker.UntillEge import UntillEge
    notify_observer = NotifyCheckerObserver()
    notify_observer.add_items(UntillEge('18-05-28'))
    notify_observer.execute()
