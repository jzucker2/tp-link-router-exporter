from enum import Enum
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from prometheus_flask_exporter import Counter, Summary, Gauge


class Labels(Enum):
    DEVICE = 'device'
    SCRAPE_EVENT = 'scrape_event'
    ROUTER_NAME = 'router_name'
    CONNECTION_TYPE = 'connection_type'
    DEVICE_TYPE = 'device_type'
    HOSTNAME = 'hostname'
    IP_ADDRESS = 'ip_address'
    MAC_ADDRESS = 'mac_address'
    PACKET_ACTION = 'packet_action'
    FIRMWARE_PROPERTY = 'firmware_property'
    FIRMWARE_VALUE = 'firmware_value'
    HARDWARE_VERSION = 'hardware_version'
    MODEL = 'model'
    FIRMWARE_VERSION = 'firmware_version'
    LEASE_TIME = 'lease_time'

    @classmethod
    def labels(cls):
        return list([
            cls.DEVICE.value,
        ])

    @classmethod
    def basic_router_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
        ])

    @classmethod
    def firmware_router_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.HARDWARE_VERSION.value,
            cls.MODEL.value,
            cls.FIRMWARE_VERSION.value,
        ])

    @classmethod
    def client_connections_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.CONNECTION_TYPE.value,
        ])

    @classmethod
    def default_device_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.DEVICE_TYPE.value,
            cls.HOSTNAME.value,
            cls.IP_ADDRESS.value,
            cls.MAC_ADDRESS.value,
        ])

    @classmethod
    def default_ipv4_dhcp_lease_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.HOSTNAME.value,
            cls.IP_ADDRESS.value,
            cls.MAC_ADDRESS.value,
            cls.LEASE_TIME.value,
        ])

    @classmethod
    def default_ipv4_reservation_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.HOSTNAME.value,
            cls.IP_ADDRESS.value,
            cls.MAC_ADDRESS.value,
        ])

    @classmethod
    def device_packets_labels(cls):
        final_labels = cls.default_device_labels()
        final_labels.extend([
            cls.PACKET_ACTION.value,
        ])
        return list(final_labels)

    @classmethod
    def scrape_event_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.SCRAPE_EVENT.value,
        ])


class Metrics(object):
    DEBUG_ROUTE_TIME = Summary(
        'tp_link_router_exporter_debug_route_time',
        'Time spent to handle debug route request')

    DEBUG_ROUTE_EXCEPTIONS = Counter(
        'tp_link_router_exporter_debug_route_exceptions',
        'Exceptions while attempting to handle debug route request')

    TP_LINK_ROUTER_TEST_TIME = Summary(
        'tp_link_router_exporter_router_test_time',
        'Time spent to get quick info from TP-Link router')

    TP_LINK_ROUTER_TEST_EXCEPTIONS = Counter(
        'tp_link_router_exporter_router_test_exceptions',
        'Exceptions while attempting to get quick info from TP-Link router')

    SIMPLE_COLLECTOR_ROUTE_TIME = Summary(
        'tp_link_router_exporter_simple_collector_route_time',
        'Time spent to handle simple collector route request')

    SIMPLE_EXPORTER_ROUTE_EXCEPTIONS = Counter(
        'tp_link_router_exporter_simple_collector_route_exceptions',
        'Exceptions while attempting to handle simple collector route request')

    COLLECTOR_METRICS_UPDATE_ROUTE_TIME = Summary(
        'tp_link_router_exporter_collector_metrics_update_route_time',
        'Time spent to handle collector metrics update route request')

    COLLECTOR_METRICS_UPDATE_ROUTE_EXCEPTIONS = Counter(
        'tp_link_router_exporter_collector_metrics_update_route_exceptions',
        'Exceptions while attempting collector metrics update route request')

    ROUTER_SCRAPE_EVENT_COLLECTOR_COUNTER = Counter(
        'tp_link_router_exporter_scrape_event_collector_count',
        'The count of events related to scraping a router by collector',
        Labels.scrape_event_labels()
    )

    # router specific stats

    ROUTER_CONNECTED_CLIENTS_TOTAL = Gauge(
        'tp_link_router_exporter_router_connected_clients_total',
        'The number of clients (by type) connected to this router',
        Labels.client_connections_labels())

    ROUTER_MEMORY_USAGE = Gauge(
        'tp_link_router_exporter_router_memory_usage',
        'The memory usage of the router',
        Labels.basic_router_labels())

    ROUTER_CPU_USAGE = Gauge(
        'tp_link_router_exporter_router_cpu_usage',
        'The cpu usage of the router',
        Labels.basic_router_labels())

    ROUTER_WAN_IPV4_UPTIME = Gauge(
        'tp_link_router_exporter_router_wan_ipv4_uptime',
        'The uptime (s) of the router IPv4 WAN',
        Labels.basic_router_labels())

    # router info

    ROUTER_FIRMWARE_INFO = Gauge(
        'tp_link_router_exporter_router_firmware_info',
        'The info dict of firmware on the router',
        Labels.firmware_router_labels())

    # device tracking

    ROUTER_DEVICE_PACKETS_TOTAL = Gauge(
        'tp_link_router_exporter_device_packets_total',
        'The number of packets sent or received by device on router',
        Labels.device_packets_labels())

    ROUTER_DEVICE_CONNECTED_STATUS = Gauge(
        'tp_link_router_exporter_device_connected_status',
        'This is set to 1 when a device is connected to this router',
        Labels.default_device_labels())

    # IPv4

    ROUTER_IPV4_RESERVATION_ENABLED = Gauge(
        'tp_link_router_exporter_router_ipv4_reservation_enabled',
        'This is the enabled state of an IPv4 reservation',
        Labels.default_ipv4_reservation_labels())

    ROUTER_IPV4_DHCP_LEASE_INFO = Gauge(
        'tp_link_router_exporter_router_ipv4_dhcp_lease_info',
        'This is an info dict for an IPv4 DHCP lease',
        Labels.default_ipv4_dhcp_lease_labels())


# https://github.com/rycus86/prometheus_flask_exporter#app-factory-pattern
# https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-app-factory/app_setup.py
def get_metrics_app_factory():
    return GunicornPrometheusMetrics.for_app_factory()


metrics = get_metrics_app_factory()
