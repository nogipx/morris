from commands.core.Command import Command


class HelpCommand(Command):

    def __init__(self):
        super().__init__()
        self.commands = []
        self.triggers = ['.h', '.help']

        self.system = True
        self.description = "Показ этого сообщения."

    def proceed(self, member, message, attachments, group, **kwargs):
        commands = kwargs["commands"]
        help = "Реализованы следующие команды:\n\n"
        admins = group.get_member_ids(admins=True, moders=True)
        i = 0
        for command in commands:
            if command.privilege and member.id not in admins:
                continue
            help += "{}) {}\n\n".format(i + 1, command.name())
            i += 1
        group.send(member.id, help)
        return True
