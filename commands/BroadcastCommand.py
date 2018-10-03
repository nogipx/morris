from commands.Command import Command


class BroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.mb']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        for i in self.triggers:
            body = self.command_body(i, message)
            if body:
                group.broadcast(group.get_member_ids(), body, group.parse_attachments(attachments))

        return True


class AdminBroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.ab']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        for i in self.triggers:
            body = self.command_body(i, message)
            if body:
                group.broadcast(group.get_member_ids(admins=True), body, group.parse_attachments(attachments))

        return True