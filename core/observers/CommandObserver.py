from core.observers.AbstractObserver import AbstractObserver


class CommandObserver(AbstractObserver):

    def execute(self, member, message, attachments, group, unlock, *args, **kwargs):

        group.api.messages.setActivity(user_id=member.id, type="typing")
        for command in self.commands:

            for trigger in command.triggers:

                if command.will_triggered(trigger, message):
                    body = command.command_body(command.triggers, message)

                    if command.proceed(member, body, attachments, group, trigger=trigger, *args, **kwargs):
                        unlock(member.id)
