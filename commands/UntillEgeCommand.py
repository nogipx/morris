from commands.interface import ICommand
import datetime


class UntillEge(ICommand):

    def __init__(self, ege_date):
        super().__init__()
        self._triggers = ['ue', 'Ue']
        self.ege_day = datetime.datetime.strptime(ege_date, '%y-%m-%d')
        self.ege_yday = self.ege_day.timetuple().tm_yday

    def proceed(self, *args, **kwargs):
        if len(args) > 0 and args[1] in self._triggers:
            today = datetime.date.today().timetuple()
            month = today.tm_mon
            yday = today.tm_yday

            if month > 7:
                return

            def day_msg(left_days):
                last_num = int(str(left_days)[-1])
                if last_num == 1:
                    return 'день'
                elif 2 <= last_num <= 4:
                    return 'дня'
                elif 5 <= last_num <= 9:
                    return 'дней'

            message = 'До начала экзаменов {left} {num_day} {day_msg}.' \
                .format(left='остался' if str(yday)[-1] == '1' else 'осталось',
                        day_msg=day_msg(self.ege_yday - yday),
                        num_day=self.ege_yday - yday)
            return message
        return False
