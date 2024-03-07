import yaml
from flask import current_app as app


log = app.logger


class ConfigParserException(Exception):
    pass


class ConfigParser(object):
    DEFAULT_CONFIG_FILE_PATH = 'exporter_config.yaml'

    @classmethod
    def get_config_file_path(cls):
        return cls.DEFAULT_CONFIG_FILE_PATH

    @classmethod
    def get_config_file(cls, config_file_path=None):
        if not config_file_path:
            config_file_path = cls.get_config_file_path()
        with open(config_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config

    @classmethod
    def import_config(cls, config_file_path=None):
        config = cls.get_config_file(config_file_path=config_file_path)
        return config
