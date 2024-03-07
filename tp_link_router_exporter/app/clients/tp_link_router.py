import os
from flask import current_app as app
from tplinkrouterc6u import TplinkRouterProvider


log = app.logger


ROUTER_IP = os.environ.get('TP_LINK_ROUTER_IP')
ROUTER_USERNAME = os.environ.get('TP_LINK_ROUTER_USERNAME')
ROUTER_PASSWORD = os.environ.get('TP_LINK_ROUTER_PASSWORD')


# https://github.com/AlexandrErohin/TP-Link-Archer-C6U


class TPLinkRouterException(Exception):
    pass


class TPLinkRouter(object):
    @classmethod
    def get_client(cls):
        return cls()

    @classmethod
    def get_default_router_ip(cls):
        return ROUTER_IP

    @classmethod
    def get_default_router_username(cls):
        return ROUTER_USERNAME

    @classmethod
    def get_default_router_password(cls):
        return ROUTER_PASSWORD

    def __init__(self, **kwargs):
        router_ip = kwargs.get(
            'router_ip',
            self.get_default_router_ip())
        self.router_ip = router_ip
        router_username = kwargs.get(
            'router_username',
            self.get_default_router_username())
        self.router_username = router_username
        router_password = kwargs.get(
            'router_password',
            self.get_default_router_password())
        self.router_password = router_password
        i_m = (f'logging in at router_ip: {router_ip} '
               f'with router_password: {router_password}')
        log.info(i_m)
        self.router = TplinkRouterProvider.get_client(
            router_ip,
            router_password)

    def test_debug(self):
        log.info('test_debug')
        try:
            # authorizing
            a_m = (f'attempting to authorize at '
                   f'self.router_ip: {self.router_ip}')
            log.info(a_m)
            if self.router.authorize():
                sa_m = (f'self.router_ip: {self.router_ip} '
                        f'succeeded at auth')
                log.info(sa_m)
                # Get firmware info - returns Firmware
                firmware = self.router.get_firmware()
                log.info(f'router firmware: {firmware}')

                # Get status info - returns Status
                status = self.router.get_status()
                log.info(f'router status: {status}')
        except Exception as unexp:
            u_m = (f'self.router_ip: {self.router_ip} '
                   f'got exception unexp: {unexp}')
            log.info(u_m)

        finally:
            # always logout as TP-Link Web
            # Interface only supports upto 1 user logged
            l_m = f'now logging out from self.router_ip: {self.router_ip}'
            log.info(l_m)
            self.router.logout()
