from enum import Enum


class ScrapeEvents(Enum):
    AUTHORIZE = 'authorize'
    LOGOUT = 'logout'
    GET_FIRMWARE = 'get_firmware'
    GET_STATUS = 'get_status'
    GET_DEVICES = 'get_devices'
    GET_IPV4_STATUS = 'get_ipv4_status'
    GET_IPV4_RESERVATIONS = 'get_ipv4_reservations'
    GET_IPV4_DHCP_LEASES = 'get_ipv4_dhcp_leases'
    ATTEMPT_GET_ROUTER_METRICS = 'attempt_get_router_metrics'
    SUCCESS = 'success'
    ERROR = 'error'
