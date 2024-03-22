from enum import Enum
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from prometheus_flask_exporter import Counter, Summary, Gauge


class Labels(Enum):
    DEVICE = 'device'
    SCRAPE_EVENT = 'scrape_event'
    ROUTER_NAME = 'router_name'
    CONNECTION_TYPE = 'connection_type'
    FIRMWARE_PROPERTY = 'firmware_property'
    FIRMWARE_VALUE = 'firmware_value'

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
            cls.FIRMWARE_PROPERTY.value,
            cls.FIRMWARE_VALUE.value,
        ])

    @classmethod
    def client_connections_labels(cls):
        return list([
            cls.ROUTER_NAME.value,
            cls.CONNECTION_TYPE.value,
        ])

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

    # info

    ROUTER_FIRMWARE_PROPERTY = Gauge(
        'tp_link_router_exporter_router_firmware_property',
        'The value of a firmware property on the router',
        Labels.firmware_router_labels())


# https://github.com/rycus86/prometheus_flask_exporter#app-factory-pattern
# https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-app-factory/app_setup.py
def get_metrics_app_factory():
    return GunicornPrometheusMetrics.for_app_factory()


metrics = get_metrics_app_factory()
