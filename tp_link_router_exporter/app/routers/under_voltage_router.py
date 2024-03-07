from flask import current_app as app
from ..clients.rpi_bad_power import RPiBadPower
from ..metrics import Metrics
from .router import Router, RouterException


log = app.logger


class UnderVoltageRouterException(RouterException):
    pass


class UnderVoltageRouter(Router):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rpi_bad_power = RPiBadPower.get_client()

    @property
    def service(self):
        return 'check_under_voltage'

    @Metrics.UNDER_VOLTAGE_CHECK_TIME.time()
    def check_under_voltage_response(self):
        with Metrics.UNDER_VOLTAGE_CHECK_EXCEPTIONS.count_exceptions():
            p_m = 'check for under_voltage'
            log.debug(p_m)
            final_response = self.base_response('check_under_voltage')
            self.rpi_bad_power.check_under_voltage()
            return final_response
