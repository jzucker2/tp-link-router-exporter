from flask import current_app as app
from ..clients.rpi_bad_power import RPiBadPower
from ..metrics import Metrics
from .router import Router, RouterException


log = app.logger


class DebugRouterException(RouterException):
    pass


class DebugRouter(Router):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rpi_power_client = RPiBadPower.get_client()

    @property
    def service(self):
        return 'debug'

    @Metrics.DEBUG_ROUTE_TIME.time()
    def handle_debug_route_response(self):
        with Metrics.DEBUG_ROUTE_EXCEPTIONS.count_exceptions():
            p_m = 'handle debug route'
            log.debug(p_m)
            final_response = self.base_response('debug')
            result = self.rpi_power_client.check_under_voltage()
            log.info(f'result: {result}')
            if result:
                final_response['rpi_bad_power'] = result
            return final_response
