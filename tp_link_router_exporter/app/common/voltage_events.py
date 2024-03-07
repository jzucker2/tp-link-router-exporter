from enum import Enum


class VoltageEventsException(Exception):
    pass


class VoltageEvents(Enum):
    UNDER_VOLTAGE_DETECTED = 'under_voltage'
    NORMAL = 'normal'
    SYSTEM_NOT_SUPPORTED = 'system_not_supported'
    MISSING = 'missing'

    @property
    def event_name(self):
        return self.value

    @property
    def under_voltage_value(self):
        if self == self.NORMAL:
            return 0
        elif self == self.UNDER_VOLTAGE_DETECTED:
            return 1
        e_m = f'Encountered invalid voltage event for value self: {self}'
        raise VoltageEventsException(e_m)
