from commands import Command


class HelpCommand(Command):

    def __init__(self):
        super().__init__()
        self._triggers = ['help', 'Help']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        print('PROCEED_HELP: ', args)
        if len(args) > 2 and args[2]:
            sub_cmd = args[2]
            if sub_cmd == 'ege':
                return self.help_ege()
            elif sub_cmd == 'me':
                return self.help_me()
        elif len(args) == 2:
            return self.all_commands()
        return False

    def all_commands(self):
        commands = """
На данный момент доступны следующие команды:

@ help -  
# вывод этого меню

@ t    -  
# расписание на завтра

@ tt   -  
# расписание на всю неделю

@ hw   -  
# получение домашних заданий из группы

@ ege  -  задачник ЕГЭ (РешуЕГЭ)
@ полное описание команды - 'help ege'

@ me   -  настройка оповещений
# полное описание команды - 'help me' :D

@ about - 
# информация об авторе и целях создания
        """
        return commands

    def help_ege(self):
        ege = """
Команды для задачника ЕГЭ:
@
@
@
        """
        return ege

    def help_me(self):
        me = """
Команды для настройки записи о пользователе:
@
@
@
        """
        return me

if __name__ == '__main__':
    help = HelpCommand()
    help.handle(1786784, 'help')