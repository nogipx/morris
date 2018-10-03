from core.handlers.EventHandler import EventHandler
from vk_communicate.BotAccount import BotAccount
from vk_communicate.group_manager import Group

from commands import UntillEge
from core.observers import NotifyCheckerObserver, AbstractObserver

from commands import HelpCommand
from commands.AboutCommand import AboutCommand
from core.observers import CommandObserver
from commands import HomeworkCommand
from commands import EgeShellCommand

from database import Member
from database.DBProxy import DBProxy

import argparse


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


parser = argparse.ArgumentParser('Settings for Morris Bot')
parser.add_argument('-T', '--token', help='Token which you got from your group admin.')
parser.add_argument('-Pl', '--parser-login',
                    help='Login for your bot-account. Opens new feature like a parsing timetable')
parser.add_argument('-Pp', '--parser-password',
                    help='Password for your bot-account.')
args = vars(parser.parse_args())


bot = EventHandler()
token = args.get('token')

# Creating group-class
group = Group()
group.auth(token)
group.connect_storage(DBProxy(Member))

bot.set_group(group)

# Setup account for bot. This is need for parsing group wall and timetable
account = BotAccount.get_account()
account.auth(args.get('parser-login'), args.get('parser-password'))

# Setup observers that handle commands
command_observer = AbstractObserver.get_observer(CommandObserver)
notify_observer = AbstractObserver.get_observer(NotifyCheckerObserver)
notify_observer.set_group(group)

# =================================================================
# Setup commands
time = '18:05'
# Timetable
tt_time = ('7:00', '20:00')
# timetable = setup_command(TopicTimetableCommand, group.group_id, account, time=tt_time)

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
    about, help, ege, untill_ege, hw, #timetable
]

command_observer.add(*commands)

notify_observer.add(*commands)

# Adding observers into bot
bot.set_command_observer(command_observer)
bot.set_command_checker(notify_observer)

# Start mainloop
bot.listen()

