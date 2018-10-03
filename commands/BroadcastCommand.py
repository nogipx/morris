from commands.Command import Command


class BroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['/b']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        for i in self.triggers:
            if self.will_triggered(i, message):
                group.broadcast(group.get_member_ids(), self.get_body(i, message), group.parse_attachments(attachments))


class AdminBroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['/a']

    def proceed(self, member, message, attachments, group, *args, **kwargs):
        for i in self.triggers:
            if self.will_triggered(i, message):
                group.broadcast(group.get_member_ids(admins=True), self.get_body(i, message), group.parse_attachments(attachments))