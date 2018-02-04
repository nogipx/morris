import argparse, configparser
from Bot import Bot
from BotAccount import BotAccount
from modules.interfaces.IObserver import IObserver
from modules.group_manager.GroupManager import GroupManager

from modules.notify_checker.UntillEge import UntillEge
from modules.notify_checker.NotifyCheckObserver import NotifyCheckerObserver

from modules.commands.HelpCommand import HelpCommand
from modules.commands.AboutCommand import AboutCommand
from modules.commands.CommandObserver import CommandObserver
from modules.commands.HomeworkCommand import HomeworkCommand
from modules.commands.EgeShellCommand import EgeShellCommand
from modules.commands.TopicTimetableCommand import TopicTimetableCommand


def setup_command(cmd_class, *class_args, all_week=False, **kwargs):
    cmd_object = cmd_class(*class_args)
    if all_week:
        cmd_object.add_activate_wday(all_week=True)
    for key in kwargs:
        value = kwargs.get(key)
        if key == 'days':
            cmd_object.clear(key)
            if not isinstance(value, int):
                cmd_object.add_activate_wday(*value)
                continue
            cmd_object.add_activate_wday(value)
        if key == 'time':
            if not isinstance(value, str):
                cmd_object.add_activate_time(*value)
                continue
            cmd_object.add_activate_time(value)
    cmd_object.generate_name()
    return cmd_object


def weekdays(*wdays):
    data = {
        "Воскресенье": 6,
        "Понедельник": 0,
        "Вторник": 1,
        "Среда": 2,
        "Четверг": 3,
        "Пятница": 4,
        "Суббота": 5,
    }
    result = []
    for day in wdays:
        result.append(data.get(day))
    return result


bot = Bot()
token = '7134ec6b881f83f140dcbdd6a0e0e3001300a2b9f69bc5d13341d0bf650797564141ed907b2dcf8df1e93'
# token = 'fc9d1694e5e9ca322c9fd6183c234b131db64335708a8c82856e8b9a14956184fc89e9863f16c54db2d08'

# Creating group-class
group = GroupManager()
# group.add_activate_time('6:00', '8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00')
# group.add_activate_wday(all_week=True)
# group.add_activate_time('21:28', '21:29')
group.auth(token)
bot.set_group_api(group)

# Setup account for bot. This is need for parsing group wall and timetable
account = BotAccount.get_account()
account.auth('89884095357', 'HokingBH98')
bot.set_account_api(account)

# Setup observers that handle commands
command_observer = IObserver.get_observer(CommandObserver)
notify_observer = IObserver.get_observer(NotifyCheckerObserver)
notify_observer.set_group(group)

# =================================================================
# Setup commands
time = '18:05'
# Timetable
tt_time = ('20:00')
timetable = setup_command(TopicTimetableCommand, group.group_id, account, time=tt_time)

# Ege shell
ege = setup_command(EgeShellCommand, group)

# Timer untill EGE
ue_time = ('9:00', '22:29')
ue_days = weekdays('Вторник')
ege_day = '18-05-28'
untill_ege = setup_command(UntillEge, ege_day, time=ue_time, days=ue_days)

# Homework
hw = setup_command(HomeworkCommand, account, group.group_id)
# hw_time = ('6:00', '20:00')
# hw.add_activate_time(hw_time)

# Help and About
help = setup_command(HelpCommand)
about = setup_command(AboutCommand)

# =================================================================
# Adding command modules in particular handlers(observers)
commands = [
    about, help, ege, untill_ege, hw, timetable
]

command_observer.add_items(*commands)

notify_observer.add_items(*commands)

# Adding observers into bot
bot.set_command_observer(command_observer)
bot.set_command_checker(notify_observer)

# Start mainloop
bot.listen()

