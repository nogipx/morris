#!/usr/bin/python3
# -*- coding: utf-8 -*-
import configparser
import argparse
import os

FIVE_DAYS = False


def five_days():
    global FIVE_DAYS
    FIVE_DAYS = True


def generate_config(path):
    config = configparser.ConfigParser()
    if os.path.exists(path):
        print('Config {} exists'.format(path))
        exit(0)
    # settings config
    config.add_section('settings')
    config.set('settings', 'token', '')
    config.set('settings', 'group_id', '')
    config.set('settings', 'exclude', '')

    # group_bot config
    config.add_section('posts_parser')
    config.set('posts_parser', 'login', '')
    config.set('posts_parser', 'password', '')

    # timetable config
    config.add_section('timetable')
    work_days = ''
    days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
    if FIVE_DAYS:
        days = days[:-1]
    for day in days:
        config.set('timetable', day, '')
        work_days += '{},'.format(day)
    config.set('timetable', 'work_days', work_days[:-1])

    with open(path, 'w') as config_file:
        config.write(config_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('-five', action='store_const', const=five_days, default=False, dest='five_days')
    args = vars(parser.parse_args())
    if args.get('five_days'):
        five_days()
    generate_config(args.get('path'))