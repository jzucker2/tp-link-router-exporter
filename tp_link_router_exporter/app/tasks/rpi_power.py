from flask import current_app as app
from ..extensions import scheduler
from ..routers.collector_router import CollectorRouter
from .rpi_power_pinger import RPiPowerPinger


log = app.logger


# TODO: make this configurable and turn and off as well
@scheduler.task(
    "interval",
    id="rpi_power_metrics_update",
    seconds=RPiPowerPinger.get_metrics_interval_seconds(),
    max_instances=1,
    start_date="2000-01-01 12:19:00",
)
def perform_rpi_power_metrics_update():
    """RPi Power metrics update

    Added when app starts.
    """
    pu_m = "running rpi_power_metrics_update!"
    log.debug(pu_m)

    with scheduler.app.app_context():
        router = CollectorRouter()
        response = router.handle_collector_metrics_update_route_response()
        r_m = f'scheduled rpi power metrics update got response: {response}'
        log.debug(r_m)
