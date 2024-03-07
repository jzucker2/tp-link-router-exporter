import os


ROUTER_IP = os.environ.get('TP_LINK_ROUTER_IP')
ROUTER_NAME = os.environ.get('TP_LINK_ROUTER_NAME')
ROUTER_USERNAME = os.environ.get('TP_LINK_ROUTER_USERNAME')
ROUTER_PASSWORD = os.environ.get('TP_LINK_ROUTER_PASSWORD')
ROUTER_IP_2 = os.environ.get('TP_LINK_ROUTER_IP_2')
ROUTER_NAME_2 = os.environ.get('TP_LINK_ROUTER_NAME_2')
ROUTER_USERNAME_2 = os.environ.get('TP_LINK_ROUTER_USERNAME_2')
ROUTER_PASSWORD_2 = os.environ.get('TP_LINK_ROUTER_PASSWORD_2')


class EnvVars(object):
    @classmethod
    def get_default_router_ip(cls):
        return ROUTER_IP

    @classmethod
    def get_default_router_name(cls):
        return ROUTER_NAME

    @classmethod
    def get_default_router_username(cls):
        return ROUTER_USERNAME

    @classmethod
    def get_default_router_password(cls):
        return ROUTER_PASSWORD

    @classmethod
    def get_secondary_router_ip(cls):
        return ROUTER_IP_2

    @classmethod
    def get_secondary_router_name(cls):
        return ROUTER_NAME_2

    @classmethod
    def get_secondary_router_username(cls):
        return ROUTER_USERNAME_2

    @classmethod
    def get_secondary_router_password(cls):
        return ROUTER_PASSWORD_2
