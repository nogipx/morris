from EventHandler import EventHandler
from BotAccount import BotAccount
from modules.commands.interface.IObserver import IObserver
from modules.group_manager.Group import Group

from modules.commands.UntillEgeCommand import UntillEge
from modules.commands.observers.NotifyCheckObserver import NotifyCheckerObserver

from modules.commands.HelpCommand import HelpCommand
from modules.commands.AboutCommand import AboutCommand
from modules.commands.observers.CommandObserver import CommandObserver
from modules.commands.HomeworkCommand import HomeworkCommand
from modules.commands.EgeShellCommand import EgeShellCommand
from modules.commands.TopicTimetableCommand import TopicTimetableCommand

from modules.database.UserORM import Member
from modules.database.DBProxy import DBProxy

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
storage = DBProxy(Member)
group.connect_storage(storage)

bot.set_group(group)

# Setup observers that handle commands
command_observer = IObserver.get_observer(CommandObserver)
notify_observer = IObserver.get_observer(NotifyCheckerObserver)
notify_observer.set_group(group)

# =================================================================
# Setup commands
from modules.march8.March8 import March8

time = ['6:00', '20:57']
days = weekdays('Пятница')
march8 = setup_command(March8, group, time=time, days=days)


# =================================================================
# Adding command modules in particular handlers(observers)
commands = [march8]

command_observer.add_items(*commands)

notify_observer.add_items(*commands)

# Adding observers into bot
bot.set_command_observer(command_observer)
bot.set_command_checker(notify_observer)

# Start mainloop
bot.listen()

