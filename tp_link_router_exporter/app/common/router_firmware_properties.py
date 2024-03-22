from enum import Enum


class RouterFirmwareProperties(Enum):
    HARDWARE_VERSION = 'hardware_version'
    MODEL = 'model'
    FIRMWARE_VERSION = 'firmware_version'

    @property
    def label_string(self):
        return self.value
