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
    def _inc_voltage_event(cls, event):
        Metrics.UNDER_VOLTAGE_EVENT_COLLECTOR_COUNTER.labels(
            event=event.value,
        ).inc()

    def check_under_voltage(self):
        pass
        # event = self.rpi_power_client.check_under_voltage()
        # self._inc_voltage_event(event)
        # if event == VoltageEvents.SYSTEM_NOT_SUPPORTED:
        #     Metrics.SYSTEM_SUPPORTED_VALUE.set(0)
        #     # TODO: would be cool to do something else here
        #     return None
        # else:
        #     Metrics.SYSTEM_SUPPORTED_VALUE.set(1)
        #     final_value = event.under_voltage_value
        #     Metrics.UNDER_VOLTAGE_VALUE.set(final_value)
        #     return final_value

    def update_rpi_power_metrics(self):
        return self.check_under_voltage()
