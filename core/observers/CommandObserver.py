from core.observers.AbstractObserver import AbstractObserver


class CommandObserver(AbstractObserver):

    __instance__ = None

    def execute(self, member, message, attachments, group, unlock, *args, **kwargs):

        for command in self.commands:

            for trigger in command.triggers:

                if command.will_triggered(trigger, message):
                    group.api.messages.setActivity(user_id=member.id, type="typing")
                    if command.proceed(member, message, attachments, group, *args, **kwargs):
                        unlock(member.id)
