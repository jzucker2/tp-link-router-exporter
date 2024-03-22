from enum import Enum


class RouterFirmwareProperties(Enum):
    HARDWARE_VERSION = 'hardware_version'
    MODEL = 'model'
    FIRMWARE_VERSION = 'firmware_version'

    @property
    def label_string(self):
        return self.value

    @classmethod
    def metrics_properties_list(cls):
        return list([
            cls.HARDWARE_VERSION,
            cls.MODEL,
            cls.FIRMWARE_VERSION,
        ])
