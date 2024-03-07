from flask import current_app as app
from ..clients.env_vars import EnvVars
from ..clients.collector import Collector
from ..metrics import Metrics
from .router import Router, RouterException


log = app.logger


class CollectorRouterException(RouterException):
    pass


class CollectorRouter(Router):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collector = Collector.get_collector()
        self._collectors = None

    @property
    def collectors(self):
        if not self._collectors:
            collectors = self.create_collectors()
            self._collectors = list(collectors)
        return self._collectors

    @classmethod
    def create_collectors(cls):
        collector = Collector.get_collector(
            router_ip=EnvVars.get_default_router_ip(),
            router_password=EnvVars.get_default_router_password(),
            router_name=EnvVars.get_default_router_name())
        collector_2 = Collector.get_collector(
            router_ip=EnvVars.get_secondary_router_ip(),
            router_password=EnvVars.get_secondary_router_password(),
            router_name=EnvVars.get_secondary_router_name())
        return list([
            collector,
            collector_2,
        ])

    @property
    def service(self):
        return 'collector'

    @Metrics.SIMPLE_COLLECTOR_ROUTE_TIME.time()
    def handle_simple_collector_route_response(self):
        with Metrics.SIMPLE_EXPORTER_ROUTE_EXCEPTIONS.count_exceptions():
            p_m = 'handle simple collector route'
            log.debug(p_m)
            final_response = self.base_response('simple')
            collector = Collector.get_collector()
            result = collector.get_router_metrics()
            r_m = f'self.collector: {self.collector} got result: {result}'
            log.debug(r_m)
            return final_response

    @Metrics.COLLECTOR_METRICS_UPDATE_ROUTE_TIME.time()
    def handle_collector_metrics_update_route_response(self):
        with Metrics.COLLECTOR_METRICS_UPDATE_ROUTE_EXCEPTIONS.count_exceptions():  # noqa: E501
            p_m = 'handle collector metrics update route'
            log.debug(p_m)
            final_response = self.base_response('metrics_update')
            for collector in self.collectors:
                result = collector.update_router_metrics()
                r_m = f'self.collector: {self.collector} got result: {result}'
                log.debug(r_m)
            return final_response
