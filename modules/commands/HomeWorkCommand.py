from modules.interfaces.ICommand import ICommand


class HomeWorkCommand(ICommand):

    def __init__(self):
        super().__init__()
        self._triggers = 'hw'

    def proceed(self):
        print('analyze group///')