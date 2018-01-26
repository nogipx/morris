from modules.interfaces.IShell import IShell


class ConfigShell(IShell):

    def shell_parse(self, row_input):
        super().shell_parse(row_input)

    def shell_execute(self, **kwargs):
        super().shell_execute(**kwargs)