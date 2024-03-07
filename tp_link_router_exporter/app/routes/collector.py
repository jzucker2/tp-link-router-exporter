from flask import current_app as app
from ..routers.collector_router import CollectorRouter


log = app.logger


@app.route('/api/v1/rpi/collector/simple')
@app.route('/api/v1/rpi-power/collector/simple')
def handle_simple_collector_route():
    router = CollectorRouter()
    return router.handle_simple_collector_route_response()


@app.route('/api/v1/rpi/collector/metrics/update')
@app.route('/api/v1/rpi-power/collector/metrics/update')
def handle_collector_metrics_update_route():
    router = CollectorRouter()
    return router.handle_collector_metrics_update_route_response()
