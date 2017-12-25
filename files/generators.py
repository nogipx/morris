def timetable_from_config(config):
    """ Генерация расписания из конфига """
    days = []
    try:
        days = config.get('timetable', 'work_days').split(',')
    except Exception as error:
        print(error)
    result = ''

    for day in days:
        result += '==== {day} ====\n'.format(day=day.upper())
        lessons = str(config.get('timetable', day)).split(',')
        for lesson in lessons:
            result += '— {lesson}\n'.format(lesson=lesson)
        result += '\n'

    return result