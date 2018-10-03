from commands.Command import Command


class SkippedLectionsCommand(Command):

    def __init__(self):
        super().__init__()
        self.triggers = ['.sl']

        self.inc_triggers =['.a']
        self.dec_triggers =['.d']

        self.description = "Рассчитывает процент пропусков занятий."

    def proceed(self, member, message, attachments, group, *args, **kwargs):

        dec_triggered = self.command_body(self.dec_triggers, message)

        inc_triggered = self.command_body(self.inc_triggers, message)

        if inc_triggered:
            split_msg = inc_triggered.split()
            value = split_msg[0] if len(split_msg) >= 1 and split_msg[0] else 0

            group.storage.increase_skipped(member.id, value)

            cur_skipped = group.storage.get_skipped(member.id)
            cur_percents = group.storage.skipped_percents(member.id)
            answer = "# Пропуски # \n+{} прогулов. \nТекущее кол-во: {} \nПроцент: {}".format(value, cur_skipped, cur_percents)
            group.send(member.id, answer, attachments)

        elif dec_triggered:
            split_msg = dec_triggered.split()
            value = split_msg[0] if len(split_msg) >= 1 and split_msg[0] else 0

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