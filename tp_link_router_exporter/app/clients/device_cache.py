from datetime import datetime
from flask import current_app as app


log = app.logger


# TODO: need to include date checked so I can get all the other devices
class DeviceCacheException(Exception):
    pass


class DeviceCacheValue(object):
    def __init__(self, device, update_date):
        super().__init__()
        self.device = device
        self.update_date = update_date


class DeviceCache(object):
    DATE_HASH_STRING_FORMAT = "%Y_%m_%d__%H_%M_%S"

    def __init__(self):
        super().__init__()
        self._devices = {}

    @classmethod
    def default_device_cache(cls):
        return cls()

    @classmethod
    def get_date_hash_string(cls, input_dt):
        return input_dt.strftime(cls.DATE_HASH_STRING_FORMAT)

    @property
    def devices(self):
        return self.devices

    def get_key(self, device, update_date):
        device_hash = str(device.macaddress)
        update_hash = self.get_date_hash_string(update_date)
        key = f'{device_hash}=={update_hash}'
        return key

    def add_or_update_device(self, device, update_date):
        key = self.get_key(device, update_date)
        self.devices[key] = DeviceCacheValue(device, update_date)

    def has_device(self, device, update_date):
        key = self.get_key(device, update_date)
        return bool(key in self.devices)

    def check_device(self, device, update_date):
        pass
        # if self.has_device(device, update_date):
        #     self.add_device(device, update_date)
        #     return True
        # self.add_device(device, update_date)
