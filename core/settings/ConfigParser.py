import configparser
import os

from settings import *


class ConfigParser:

    def __init__(self, config_dir):
        self.config_name = "config.ini"
        self.main_section = "core"

        self.fields = []

        self.default_fields = "login password token"
        self.add_default_fields()

        self.config_path = os.path.join(config_dir, self.config_name)

        if not os.path.exists(self.config_path):
            self.config = self.create_empty_cfg()
        else:
            self.config = self.fill_exists_cfg(self.config_path)

        self.config_dict = self.dict()

    def get_args(self):
        return self.config

    def create_empty_cfg(self):
        config = configparser.ConfigParser()

        main_section = self.main_section
        config.add_section(main_section)

        for i in self.fields:
            config[main_section][i] = ""

        self.config = config
        self.save()

        return self.config

    def fill_exists_cfg(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        return self.config

    def dict(self):
        vals = {}

        for i in self.config:
            for j in self.config[i]:
                val = self.config[i][j]
                if val:
                    vals.update({j: val})

        return vals

    def add_field(self, name):
        self.fields.append(name)

    def add_default_fields(self):
        names = self.default_fields.split()
        for i in names: self.add_field(i)

    def save(self):
        with open(self.config_path, 'w') as fp:
            self.config.write(fp)

        self.config_dict = self.dict()

    def __getitem__(self, item):
        return self.config_dict[item]


if __name__ == '__main__':
    p = ConfigParser(project_path)
    t = p.fill_exists_cfg(p.config_path)
    print(p.dict())
