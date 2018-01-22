from modules.interfaces.IObserver import IObserver
import datetime
import time


class NotifyCheckerObserver(IObserver):

    __instance__ = None

    def set_group(self, group):
        self._group = group

    def execute(self, *args):
        today = datetime.datetime.today().timetuple()
        hour, minute = today.tm_hour, str(today.tm_min)
        if len(minute) == 1:
            minute = '0' + str(minute)
        ctime = '{}:{}'.format(hour, minute)
        for command in self._commands:
            if ctime in command._when_activate:
                return command.handle()

    def loop(self):
        while True:
            message = self.execute()
            if message:
                self._group.broadcast(self._group.get_members(), message, None)
            time.sleep(58)


if __name__ == '__main__':
    from modules.notify_checker.UntillEge import UntillEge
    notify_observer = NotifyCheckerObserver()
    notify_observer.add_items(UntillEge('18-05-28'))
    notify_observer.execute()

