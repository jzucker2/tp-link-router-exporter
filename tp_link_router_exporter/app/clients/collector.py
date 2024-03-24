from datetime import datetime
from flask import current_app as app
from ..utils import global_get_now, normalize_name
from ..common.router_firmware_properties import RouterFirmwareProperties
from ..common.client_connection_types import ClientConnectionTypes
from ..common.scrape_events import ScrapeEvents
from ..common.packet_actions import PacketActions
from ..metrics import Metrics
from .tp_link_router import TPLinkRouter


log = app.logger


class CollectorException(Exception):
    pass


class CollectorFetchException(CollectorException):
    pass


class CollectorRecordException(CollectorException):
    pass


class CollectordRecordPacketActionException(CollectorRecordException):
    pass


class CollectordRecordDHCPLeaseException(CollectorRecordException):
    pass


class InvalidPacketActionCollectorException(CollectorException):
    pass


class InvalidRouterFirmwarePropertyCollectorException(CollectorException):
    pass


class InvalidClientConnectionTypeCollectorException(CollectorException):
    pass


class Collector(object):
    DEFAULT_ROUTER_NAME = 'default'
    PERMANENT_LEASE = 'Permanent'

    @classmethod
    def normalize_input(cls, input):
        return normalize_name(input)

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
            scrape_event=event.label_string,
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
        try:
            firmware = self.router_client.get_firmware()
            event = ScrapeEvents.GET_FIRMWARE
            self._inc_scrape_event(event)
            return firmware
        except Exception as unexp:
            u_m = f'get firmware got unexp: {unexp}'
            log.error(u_m)
            raise CollectorFetchException(u_m)

    def _get_status(self):
        try:
            status = self.router_client.get_status()
            event = ScrapeEvents.GET_STATUS
            self._inc_scrape_event(event)
            return status
        except Exception as unexp:
            u_m = f'get router status got unexp: {unexp}'
            log.error(u_m)
            raise CollectorFetchException(u_m)

    def _get_ipv4_status(self):
        try:
            status = self.router_client.get_ipv4_status()
            event = ScrapeEvents.GET_IPV4_STATUS
            self._inc_scrape_event(event)
            return status
        except Exception as unexp:
            u_m = f'ipv4 status got unexp: {unexp}'
            log.error(u_m)
            raise CollectorFetchException(u_m)

    def _get_ipv4_reservations(self):
        try:
            res = self.router_client.get_ipv4_reservations()
            event = ScrapeEvents.GET_IPV4_RESERVATIONS
            self._inc_scrape_event(event)
            return res
        except Exception as unexp:
            u_m = f'get ipv4 reservations got unexp: {unexp}'
            log.error(u_m)
            raise CollectorFetchException(u_m)

    def _get_ipv4_dhcp_leases(self):
        try:
            leases = self.router_client.get_ipv4_dhcp_leases()
            event = ScrapeEvents.GET_IPV4_DHCP_LEASES
            self._inc_scrape_event(event)
            return leases
        except Exception as unexp:
            u_m = f'get ipv4 dhcp leases got unexp: {unexp}'
            log.error(u_m)
            raise CollectorFetchException(u_m)

    def _get_devices(self, status):
        if not status:
            return
        devices = list(status.devices)
        event = ScrapeEvents.GET_DEVICES
        self._inc_scrape_event(event)
        return devices

    def _get_client_connection_type_value(self, status, connection_type):
        if connection_type == ClientConnectionTypes.WIRED:
            return status.wifi_clients_total
        elif connection_type == ClientConnectionTypes.WIFI:
            return status.wired_total
        elif connection_type == ClientConnectionTypes.TOTAL:
            return status.clients_total
        elif connection_type == ClientConnectionTypes.GUEST:
            return status.guest_clients_total
        e_m = f'invalid connection_type: {connection_type}'
        log.error(e_m)
        raise InvalidClientConnectionTypeCollectorException(e_m)

    def _record_connected_client_count_metrics(self, status):
        if not status:
            return
        log.debug(f'got status: {status}')
        for connection_type in ClientConnectionTypes.metrics_types_list():
            client_count = self._get_client_connection_type_value(
                status,
                connection_type)
            Metrics.ROUTER_CONNECTED_CLIENTS_TOTAL.labels(
                router_name=self.router_name,
                connection_type=connection_type.label_string,
            ).set(client_count or 0)

    def _record_status_metrics(self, status):
        if not status:
            return
        self._record_connected_client_count_metrics(status)
        # now do memory and cpu
        Metrics.ROUTER_MEMORY_USAGE.labels(
            router_name=self.router_name,
        ).set(status.mem_usage or 0)
        Metrics.ROUTER_CPU_USAGE.labels(
            router_name=self.router_name,
        ).set(status.cpu_usage or 0)
        # now WAN IPv4 uptime
        # Metrics.ROUTER_WAN_IPV4_UPTIME.labels(
        #     router_name=self.router_name,
        # ).set(status.wan_ipv4_uptime or 0)

    @classmethod
    def _get_packets_for_action(cls, device, packet_action):
        if packet_action == PacketActions.SENT:
            return device.packets_sent
        elif packet_action == PacketActions.RECEIVED:
            return device.packets_received
        else:
            pe_m = f'Invalid PacketAction for packet_action: {packet_action}'
            log.error(pe_m)
            raise InvalidPacketActionCollectorException(pe_m)

    def _record_device_packets(self, device, packet_action):
        try:
            packets = self._get_packets_for_action(device, packet_action)
            device_type = self.normalize_input(device.type)
            hostname = device.hostname
            ipaddress = str(device.ipaddress)
            macaddress = str(device.macaddress)
            d_m = (f'parsed device: {device} to get '
                   f'device_type: {device_type}, '
                   f'hostname: {hostname}, '
                   f'ipaddress: {ipaddress}, '
                   f'macaddress: {macaddress}, '
                   f'packet_action: {packet_action}, '
                   f'packets: {packets}')
            log.debug(d_m)
            Metrics.ROUTER_DEVICE_PACKETS_TOTAL.labels(
                router_name=self.router_name,
                device_type=device_type,
                hostname=hostname,
                ip_address=ipaddress,
                mac_address=macaddress,
                packet_action=packet_action.label_string,
            ).set(packets or 0)
        except Exception as unexp:
            u_m = f'recording packets got unexp: {unexp}'
            log.error(u_m)
            raise CollectordRecordPacketActionException(u_m)

    def _record_device_metrics(self, device):
        device_type = self.normalize_input(device.type)
        hostname = device.hostname
        ipaddress = str(device.ipaddress)
        macaddress = str(device.macaddress)
        Metrics.ROUTER_DEVICE_CONNECTED_STATUS.labels(
            router_name=self.router_name,
            device_type=device_type,
            hostname=hostname,
            ip_address=ipaddress,
            mac_address=macaddress,
        ).set(1)
        for packet_action in PacketActions.metrics_actions_list():
            self._record_device_packets(device, packet_action)

    def _record_devices_metrics(self, devices):
        if not devices:
            return
        d_m = f'devices metrics to parse devices: {devices}'
        log.debug(d_m)
        for device in devices:
            log.debug(f'recording metrics for device: {device}')
            self._record_device_metrics(device)

    def _get_firmware_property_value(self, firmware, property):
        if property == RouterFirmwareProperties.HARDWARE_VERSION:
            return firmware.hardware_version
        elif property == RouterFirmwareProperties.MODEL:
            return firmware.model
        elif property == RouterFirmwareProperties.FIRMWARE_VERSION:
            return firmware.firmware_version
        e_m = f'invalid firmware property: {property}'
        log.error(e_m)
        raise InvalidRouterFirmwarePropertyCollectorException(e_m)

    def _record_firmware_metrics(self, firmware):
        if not firmware:
            return
        log.debug(f'got firmware: {firmware}')
        labels = {
            'router_name': self.router_name,
        }
        for property in RouterFirmwareProperties.metrics_properties_list():
            prop_value = self._get_firmware_property_value(firmware, property)
            labels[property.label_string] = prop_value
        Metrics.ROUTER_FIRMWARE_INFO.labels(**labels).set(1)

    def _record_ipv4_status_metrics(self, ipv4_status):
        if not ipv4_status:
            return
        # FIXME: actually implement this!
        log.debug(f'got ipv4_status: {ipv4_status}')

    def _record_ipv4_reservations(self, reservations):
        if not reservations:
            return
        log.debug(f'got ipv4 reservations: {reservations}')
        for res in reservations:
            log.debug(f'recording res.enabled: {res.enabled}')
            Metrics.ROUTER_IPV4_RESERVATION_ENABLED.labels(
                router_name=self.router_name,
                hostname=res.hostname,
                ip_address=str(res.ipaddress),
                mac_address=str(res.macaddress),
            ).set(res.enabled)

    @classmethod
    def _is_dhcp_lease_permanent(cls, lease_time):
        if not lease_time:
            return False
        if lease_time == cls.PERMANENT_LEASE:
            return True
        return False

    @classmethod
    def _convert_dhcp_lease_time(cls, lease_time):
        if not lease_time:
            return 0
        # https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string  # noqa: E501
        return datetime.strptime(lease_time, "%H:%M:%S")

    def _record_dhcp_lease(self, lease):
        try:
            lease_time = lease.lease_time
            log.info(f'recording lease_time: {lease_time}')
            if self._is_dhcp_lease_permanent(lease_time):
                Metrics.ROUTER_IPV4_DHCP_PERMANENT_LEASE_INFO.labels(
                    router_name=self.router_name,
                    hostname=lease.hostname,
                    ip_address=str(lease.ipaddress),
                    mac_address=str(lease.macaddress),
                ).set(1)
            else:
                converted_lease_time = self._convert_dhcp_lease_time(
                    lease_time)
                Metrics.ROUTER_IPV4_DHCP_LEASE_TIME_SECONDS.labels(
                    router_name=self.router_name,
                    hostname=lease.hostname,
                    ip_address=str(lease.ipaddress),
                    mac_address=str(lease.macaddress),
                ).set(converted_lease_time)
        except Exception as unexp:
            u_m = f'recording dhcp lease got unexp: {unexp}'
            log.error(u_m)
            raise CollectordRecordDHCPLeaseException(u_m)

    def _record_ipv4_dhcp_leases(self, leases):
        if not leases:
            return
        log.debug(f'got ipv4 dhcp leases: {leases}')
        for lease in leases:
            self._record_dhcp_lease(lease)

    def _get_and_record_firmware(self):
        try:
            # Get firmware info - returns Firmware
            firmware = self._get_firmware()
            log.debug(f'router firmware: {firmware}')
            self._record_firmware_metrics(firmware)
        except CollectorFetchException as cfe:
            log.warning(f'cannot record firmware due to cfe: {cfe}')
        except Exception as unexp:
            u_m = f'record firmware got unexp: {unexp}'
            log.error(u_m)
            raise CollectorRecordException(u_m)

    def _get_and_record_status_and_devices(self):
        try:
            # Get status info - returns Status
            status = self._get_status()
            log.debug(f'router status: {status}')
            self._record_status_metrics(status)
            devices = self._get_devices(status)
            self._record_devices_metrics(devices)
        except CollectorFetchException as cfe:
            log.warning(f'cannot record status and devices due to cfe: {cfe}')
        except Exception as unexp:
            u_m = f'record status and devices got unexp: {unexp}'
            log.error(u_m)
            raise CollectorRecordException(u_m)

    def _get_and_record_ipv4_status(self):
        try:
            # Get IPv4 status
            # FIXME: get_ipv4_status raises an exception in underlying client
            ipv4_status = self._get_ipv4_status()
            log.info(f'router ipv4_status: {ipv4_status}')
            self._record_ipv4_status_metrics(ipv4_status)
        except CollectorFetchException as cfe:
            log.warning(f'cannot record ipv4 status due to cfe: {cfe}')
        except Exception as unexp:
            u_m = f'record ipv4 status got unexp: {unexp}'
            log.error(u_m)
            raise CollectorRecordException(u_m)

    def _get_and_record_ipv4_reservations(self):
        try:
            # Get IPv4 reservations
            ipv4_reservations = self._get_ipv4_reservations()
            log.debug(f'router ipv4_reservations: {ipv4_reservations}')
            self._record_ipv4_reservations(ipv4_reservations)
        except CollectorFetchException as cfe:
            log.warning(f'cannot record ipv4 reservations due to cfe: {cfe}')
        except Exception as unexp:
            u_m = f'record ipv4 reservations got unexp: {unexp}'
            log.error(u_m)
            raise CollectorRecordException(u_m)

    def _get_and_record_ipv4_dhcp_leases(self):
        try:
            # Get IPv4 dhcp leases
            ipv4_leases = self._get_ipv4_dhcp_leases()
            log.debug(f'router ipv4_leases: {ipv4_leases}')
            self._record_ipv4_dhcp_leases(ipv4_leases)
        except CollectorFetchException as cfe:
            log.warning(f'cannot record ipv4 dhcp leases due to cfe: {cfe}')
        except Exception as unexp:
            u_m = f'record ipv4 dhcp leases got unexp: {unexp}'
            log.error(u_m)
            raise CollectorRecordException(u_m)

    # actual part where we decide what metrics to scrape
    def _get_and_record_router_metrics(self):
        log.debug('_get_router_metrics')
        self._inc_scrape_event(ScrapeEvents.ATTEMPT_GET_ROUTER_METRICS)
        # authorizing
        a_m = (f'attempting to actually get metrics at '
               f'self.router_ip: {self.router_ip}')
        log.debug(a_m)

        # now actually get and record metrics
        self._get_and_record_firmware()
        # FIXME: need to work on IPv4 status
        # self._get_and_record_ipv4_status()
        self._get_and_record_status_and_devices()
        self._get_and_record_ipv4_reservations()
        self._get_and_record_ipv4_dhcp_leases()

    # handles flow, including log in/out
    def _execute_get_router_metrics(self):
        log.debug('_get_router_metrics')
        self._inc_scrape_event(ScrapeEvents.START_ROUTER_SCRAPE_FLOW)
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
