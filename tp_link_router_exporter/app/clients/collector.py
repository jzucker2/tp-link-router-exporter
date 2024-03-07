import dataclasses
from flask import current_app as app
from ..utils import global_get_now
from ..common.scrape_events import ScrapeEvents
from ..metrics import Metrics
from .tp_link_router import TPLinkRouter


log = app.logger


class CollectorException(Exception):
    pass


class Collector(object):
    @classmethod
    def get_client(cls, router_client=None):
        if not router_client:
            router_client = TPLinkRouter.get_client()
        return cls(router_client)

    def __init__(self, router_client):
        super().__init__()
        self.router_client = router_client
        self._last_power_value = None

    @classmethod
    def get_now(cls):
        return global_get_now()

    def __repr__(self):
        return f'Collector => blah: {self._last_power_value}'

    @classmethod
    def _inc_scrape_event(cls, event):
        Metrics.ROUTER_SCRAPE_EVENT_COLLECTOR_COUNTER.labels(
            scrape_event=event.value,
        ).inc()

    @property
    def router_ip(self):
        return self.router_client.router_ip

    def _authorize(self):
        self.router_client.authorize()
        event = ScrapeEvents.AUTHORIZE
        self._inc_scrape_event(event)

    def _logout(self):
        self.router_client.logout()
        event = ScrapeEvents.LOGOUT
        self._inc_scrape_event(event)

    def _get_firmware(self):
        firmware = self.router_client.get_firmware()
        event = ScrapeEvents.GET_FIRMWARE
        self._inc_scrape_event(event)
        return firmware

    def _get_status(self):
        status = self.router_client.get_status()
        event = ScrapeEvents.GET_STATUS
        self._inc_scrape_event(event)
        return status

    def _get_router_metrics(self):
        log.info('_get_router_metrics')
        self._inc_scrape_event(ScrapeEvents.ATTEMPT_GET_ROUTER_METRICS)
        try:
            # authorizing
            a_m = (f'attempting to authorize at '
                   f'self.router_ip: {self.router_ip}')
            log.info(a_m)
            self._authorize()
            sa_m = (f'self.router_ip: {self.router_ip} '
                    f'succeeded at auth')
            log.info(sa_m)
            # Get firmware info - returns Firmware
            firmware = self._get_firmware()
            log.info(f'router firmware: {firmware}')
            # firmware_dict = dataclasses.asdict(firmware)
            # log.info(f'firmware_dict: {firmware_dict}')

            # Get status info - returns Status
            status = self._get_status()
            log.info(f'router status: {status}')
            if status:
                clients_total = status.wifi_clients_total
                log.info(f'clients_total: {clients_total}')
                Metrics.ROUTER_WIFI_CLIENTS_TOTAL.set(
                    clients_total)
                Metrics.ROUTER_WIRED_CLIENTS_TOTAL.set(
                    status.wired_total)
                Metrics.ROUTER_CLIENTS_TOTAL.set(
                    status.clients_total)
                Metrics.ROUTER_MEMORY_USAGE.set(
                    status.mem_usage)
                Metrics.ROUTER_CPU_USAGE.set(
                    status.cpu_usage)
            status_dict = dataclasses.asdict(status)
            log.info(f'status_dict: {status_dict}')
        except Exception as unexp:
            u_m = (f'self.router_ip: {self.router_ip} '
                   f'got exception unexp: {unexp}')
            log.error(u_m)
            self._inc_scrape_event(ScrapeEvents.ERROR)

        finally:
            # always logout as TP-Link Web
            # Interface only supports upto 1 user logged
            l_m = f'now logging out from self.router_ip: {self.router_ip}'
            log.info(l_m)
            self._logout()

    def get_router_metrics(self):
        return self._get_router_metrics()

    def update_router_metrics(self):
        return self.get_router_metrics()
