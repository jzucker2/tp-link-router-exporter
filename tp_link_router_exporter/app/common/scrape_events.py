from enum import Enum


class ScrapeEvents(Enum):
    AUTHORIZE = 'authorize'
    # this is after the first metric but before devices
    UPDATE_LAST_UPDATE_DATE = 'update_last_update_date'
    LOGOUT = 'logout'
    GET_FIRMWARE = 'get_firmware'
    GET_STATUS = 'get_status'
    GET_DEVICES = 'get_devices'
    GET_IPV4_STATUS = 'get_ipv4_status'
    GET_IPV4_RESERVATIONS = 'get_ipv4_reservations'
    GET_IPV4_DHCP_LEASES = 'get_ipv4_dhcp_leases'
    START_ROUTER_SCRAPE_FLOW = 'start_router_scrape_flow'
    ATTEMPT_GET_ROUTER_METRICS = 'attempt_get_router_metrics'
    RECORD_MISSING_DEVICES = 'record_missing_devices'
    DROP_STALE_DEVICES = 'drop_stale_devices'
    SUCCESS = 'success'
    ERROR = 'error'

    @property
    def label_string(self):
        return self.value
