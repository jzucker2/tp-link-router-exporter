from enum import Enum


class ScrapeEvents(Enum):
    AUTHORIZE = 'authorize'
    # this is after the first metric but before devices
    UPDATE_LAST_UPDATE_DATE = 'update_last_update_date'
    LOGOUT = 'logout'
    LOGOUT_UNEXPECTED_ERROR = 'logout_unexpected_error'
    LOGOUT_NOT_AUTHORIZED_ERROR = 'logout_not_authorized_error'
    GET_FIRMWARE = 'get_firmware'
    GET_STATUS = 'get_status'
    GET_DEVICES = 'get_devices'
    GET_IPV4_STATUS = 'get_ipv4_status'
    GET_IPV4_RESERVATIONS = 'get_ipv4_reservations'
    GET_IPV4_DHCP_LEASES = 'get_ipv4_dhcp_leases'
    START_ROUTER_SCRAPE_FLOW = 'start_router_scrape_flow'
    ATTEMPT_GET_AUTHED_ROUTER_METRICS = \
        'attempt_get_authed_router_metrics'
    ATTEMPT_DEVICE_CACHED_ROUTER_METRICS = \
        'attempt_device_cached_router_metrics'
    RECORD_MISSING_DEVICES = 'record_missing_devices'
    DROP_ALL_STALE_DEVICES = 'drop_all_stale_devices'
    SUCCESS = 'success'
    ERROR = 'error'

    @property
    def label_string(self):
        return self.value
