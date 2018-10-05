from commands.core import Command


class HelpCommand(Command):

    def __init__(self):
        super().__init__()
        self.commands = []
        self.triggers = ['help', 'Help']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        pass

if __name__ == '__main__':
    help = HelpCommand()
    help.handle(1786784, 'help')