from flask import current_app as app
from ..utils import global_get_now
from ..common.router_firmware_properties import RouterFirmwareProperties
from ..common.client_connection_types import ClientConnectionTypes
from ..common.scrape_events import ScrapeEvents
from ..metrics import Metrics
from .tp_link_router import TPLinkRouter


log = app.logger


class CollectorException(Exception):
    pass


class Collector(object):
    DEFAULT_ROUTER_NAME = 'default'

    @classmethod
    def default_router_name(cls):
        return cls.DEFAULT_ROUTER_NAME

    @classmethod
    def get_collector(cls, router_client=None, **kwargs):
        if not router_client:
            router_client = TPLinkRouter.get_client(**kwargs)
        router_name = kwargs.get('router_name')
        if not router_name:
            router_name = cls.default_router_name()
        return cls(router_client, router_name)

    def __init__(self, router_client, router_name):
        super().__init__()
        self.router_client = router_client
        self.router_name = router_name
        self._last_power_value = None

    @classmethod
    def get_now(cls):
        return global_get_now()

    def __repr__(self):
        return f'Collector => blah: {self._last_power_value}'

    def _inc_scrape_event(self, event):
        Metrics.ROUTER_SCRAPE_EVENT_COLLECTOR_COUNTER.labels(
            router_name=self.router_name,
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

    def _get_ipv4_status(self):
        status = self.router_client.get_ipv4_status()
        event = ScrapeEvents.GET_IPV4_STATUS
        self._inc_scrape_event(event)
        return status

    def _get_ipv4_reservations(self):
        res = self.router_client.get_ipv4_reservations()
        event = ScrapeEvents.GET_IPV4_RESERVATIONS
        self._inc_scrape_event(event)
        return res

    def _get_ipv4_dhcp_leases(self):
        leases = self.router_client.get_ipv4_dhcp_leases()
        event = ScrapeEvents.GET_IPV4_DHCP_LEASES
        self._inc_scrape_event(event)
        return leases

    def _get_devices(self):
        # FIXME: not working yet
        status = self.router_client.get_ipv4_status()
        event = ScrapeEvents.GET_DEVICES
        self._inc_scrape_event(event)
        return status

    def _record_status_metrics(self, status):
        if not status:
            return
        Metrics.ROUTER_CONNECTED_CLIENTS_TOTAL.labels(
            router_name=self.router_name,
            connection_type=ClientConnectionTypes.WIFI.label_string,
        ).set(status.wifi_clients_total)
        Metrics.ROUTER_CONNECTED_CLIENTS_TOTAL.labels(
            router_name=self.router_name,
            connection_type=ClientConnectionTypes.WIRED.label_string,
        ).set(status.wired_total)
        Metrics.ROUTER_CONNECTED_CLIENTS_TOTAL.labels(
            router_name=self.router_name,
            connection_type=ClientConnectionTypes.TOTAL.label_string,
        ).set(status.clients_total)
        Metrics.ROUTER_MEMORY_USAGE.labels(
            router_name=self.router_name,
        ).set(status.mem_usage)
        Metrics.ROUTER_CPU_USAGE.labels(
            router_name=self.router_name,
        ).set(status.cpu_usage)

    def _record_devices_metrics(self, status):
        if not status:
            return
        devices = list(status.devices)
        if not devices:
            return
        d_m = f'devices from status: {status} got devices: {devices}'
        log.info(d_m)

    def _record_firmware_metrics(self, firmware):
        if not firmware:
            return
        log.debug(f'got firmware: {firmware}')
        Metrics.ROUTER_FIRMWARE_PROPERTY.labels(
            router_name=self.router_name,
            firmware_property=RouterFirmwareProperties.HARDWARE_VERSION,
            firmware_value=firmware.hardware_version,
        ).set(1)
        Metrics.ROUTER_FIRMWARE_PROPERTY.labels(
            router_name=self.router_name,
            firmware_property=RouterFirmwareProperties.MODEL,
            firmware_value=firmware.model,
        ).set(1)
        Metrics.ROUTER_FIRMWARE_PROPERTY.labels(
            router_name=self.router_name,
            firmware_property=RouterFirmwareProperties.FIRMWARE_VERSION,
            firmware_value=firmware.firmware_version,
        ).set(1)

    def _record_ipv4_status_metrics(self, ipv4_status):
        if not ipv4_status:
            return
        log.debug(f'got ipv4_status: {ipv4_status}')

    def _record_ipv4_reservations(self, reservations):
        if not reservations:
            return
        log.debug(f'got ipv4 reservations: {reservations}')

    def _record_ipv4_dhcp_leases(self, leases):
        if not leases:
            return
        log.debug(f'got ipv4 dhcp leases: {leases}')

    # actual part where we decide what metrics to scrape
    def _get_and_record_router_metrics(self):
        log.debug('_get_router_metrics')
        self._inc_scrape_event(ScrapeEvents.ATTEMPT_GET_ROUTER_METRICS)
        # authorizing
        a_m = (f'attempting to actually get metrics at '
               f'self.router_ip: {self.router_ip}')
        log.debug(a_m)
        # Get firmware info - returns Firmware
        firmware = self._get_firmware()
        log.info(f'router firmware: {firmware}')
        self._record_firmware_metrics(firmware)

        # Get status info - returns Status
        status = self._get_status()
        log.info(f'router status: {status}')
        self._record_status_metrics(status)
        self._record_devices_metrics(status)

        # # Get IPv4 status
        # ipv4_status = self._get_ipv4_status()
        # log.info(f'router ipv4_status: {ipv4_status}')
        # self._record_ipv4_status_metrics(ipv4_status)
        #
        # # Get IPv4 reservations
        # ipv4_reservations = self._get_ipv4_reservations()
        # log.info(f'router ipv4_reservations: {ipv4_reservations}')
        # self._record_ipv4_reservations(ipv4_reservations)
        #
        # # Get IPv4 dhcp leases
        # ipv4_leases = self._get_ipv4_dhcp_leases()
        # log.info(f'router ipv4_leases: {ipv4_leases}')
        # self._record_ipv4_dhcp_leases(ipv4_leases)

    # handles flow, including log in/out
    def _execute_get_router_metrics(self):
        log.debug('_get_router_metrics')
        self._inc_scrape_event(ScrapeEvents.ATTEMPT_GET_ROUTER_METRICS)
        try:
            # authorizing
            a_m = (f'attempting to authorize at '
                   f'self.router_ip: {self.router_ip}')
            log.debug(a_m)
            self._authorize()
            sa_m = (f'self.router_ip: {self.router_ip} '
                    f'succeeded at auth')
            log.debug(sa_m)
            self._get_and_record_router_metrics()
        except Exception as unexp:
            u_m = (f'self.router_ip: {self.router_ip} '
                   f'got exception unexp: {unexp}')
            log.error(u_m)
            self._inc_scrape_event(ScrapeEvents.ERROR)
        else:
            u_m = (f'self.router_ip: {self.router_ip} '
                   f'scraped successfully!')
            log.debug(u_m)
            self._inc_scrape_event(ScrapeEvents.SUCCESS)

        finally:
            # always logout as TP-Link Web
            # Interface only supports upto 1 user logged
            l_m = f'now logging out from self.router_ip: {self.router_ip}'
            log.debug(l_m)
            self._logout()

    def get_router_metrics(self):
        return self._execute_get_router_metrics()

    def update_router_metrics(self):
        return self.get_router_metrics()
