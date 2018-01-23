from modules.interfaces.ICommand import ICommand
from modules.commands.shells.EgeShell import EgeShell
from modules.group_manager.UsersStorage import UsersStorage
from threading import Thread


class EgeShellCommand(ICommand):

    def __init__(self, group):
        super().__init__()
        self._triggers = ['ege', 'Ege']
        self._group = group

    def proceed(self, *args):
        if not (len(args) >= 2):
            return
        user_id, command = args[0], args[1]
        command = command.split()
        user = UsersStorage.get_storage().find_user(user_id)
        if user and (command[0] in self._triggers):
            shell = EgeShell(self._group, user)
            if user.session_thread:
                return 'Cессия уже открыта! \n"exit" для завершения.'
            if not args:
                t = Thread(target=shell.shell_execute, args=(args,))
                t.daemon = True
                user.session_thread = t
                t.start()
        return None
