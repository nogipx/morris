from commands.core.Command import Command


class SkippedLectionsCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.sl']

        self.inc_triggers =['.a']
        self.dec_triggers =['.r']

        self.description = "Рассчитывает процент пропусков занятий."

    def proceed(self, member, message, attachments, group, **kwargs):

        dec_triggered = self.get_body(self.dec_triggers, message)

        inc_triggered = self.get_body(self.inc_triggers, message)

        if inc_triggered:
            value = self.get_value(inc_triggered)

            group.storage.increase_skipped(member.id, value)

            cur_skipped = group.storage.get_skipped(member.id)
            cur_percents = group.storage.skipped_percents(member.id)
            answer = "# Пропуски # \n+{} прогулов. \nТекущее кол-во: {} \nПроцент: {}".format(value, cur_skipped, cur_percents)
            group.send(member.id, answer, attachments)

        elif dec_triggered:
            value = self.get_value(dec_triggered)

            group.storage.decrease_skipped(member.id, value)

            cur_skipped = group.storage.get_skipped(member.id)
            cur_percents = group.storage.skipped_percents(member.id)
            answer = "# Пропуски # \n-{} прогулов. \nТекущее кол-во: {}\nПроцент: {}".format(value, cur_skipped, cur_percents)
            group.send(member.id, answer, attachments)

        else:
            cur_skipped = group.storage.get_skipped(member.id)
            cur_percents = group.storage.skipped_percents(member.id)
            answer = "# Пропуски # \nТекущее кол-во: {}\nПроцент: {}".format(cur_skipped, cur_percents)
            group.send(member.id, answer, attachments)

    def get_value(self, msg):
        split_msg = msg.split()

        if len(split_msg) == 1 and split_msg[0]:
            value = split_msg[0]

        elif len(split_msg) > 1 and split_msg[1]:
            value = split_msg[1]

        else:
            value = 0

        return value