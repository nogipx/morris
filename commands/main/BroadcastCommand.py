from commands.core.Command import Command


class BroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.mb']

        self.privilege = True
        self.description = "Рассылка сообщения всем участникам сообщества."

    def proceed(self, member, message, attachments, group, **kwargs):
        if member.id not in group.get_member_ids(admins=True, editors=True):
            group.send(member.id, "You cannot do this ^_^")
            return True

        last_message = group.get_last_message(member.id)
        group.broadcast(group.get_member_ids(), message, attachments, last_message=last_message, **kwargs)

        return True


class AdminBroadcastCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.ab']

        self.privilege = True
        self.description = "Рассылка сообщения администаторам сообщества."

    def proceed(self, member, message, attachments, group, **kwargs):
        if member.id not in group.get_member_ids(admins=True, editors=True):
            group.send(member.id, "You cannot do this ^_^")
            return True

        last_message = group.get_last_message(member.id)
        group.broadcast(
            group.get_member_ids(admins=True, editors=True),
            message, attachments, last_message=last_message, **kwargs)

        return True