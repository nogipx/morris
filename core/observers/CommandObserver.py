from core.observers.AbstractObserver import AbstractObserver
from time import sleep


class CommandObserver(AbstractObserver):

    def execute(self, member, message, attachments, group, **kwargs):

        for command in self.commands:

            for trigger in command.triggers:

                body = command.get_body(trigger, message)
                if body is not None:
                    group.api.messages.setActivity(user_id=member.id, type="typing")

                    if command.system:
                        kwargs.update({"trigger": trigger, "commands": self.commands})
                    else:
                        kwargs.update({"trigger": trigger})

                    return command.proceed(member, body, attachments, group, **kwargs)
