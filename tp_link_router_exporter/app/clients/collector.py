from flask import current_app as app
from ..utils import global_get_now
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

    def test_debug_router(self):
        return self.router_client.test_debug()

    def get_router_metrics(self):
        # self._inc_voltage_event(event)
        return self.test_debug_router()

    def update_router_metrics(self):
        return self.get_router_metrics()
