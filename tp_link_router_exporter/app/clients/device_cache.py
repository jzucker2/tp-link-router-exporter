from flask import current_app as app


log = app.logger


# TODO: need to include date checked so I can get all the other devices
class DeviceCacheException(Exception):
    pass


class DeviceCache(object):
    @classmethod
    def default_device_cache(cls):
        return cls()

    # def __init__(self, last_update_date):
    def __init__(self):
        super().__init__()
        self._devices = {}
    #     self._last_update_date = last_update_date
    #
    # @property
    # def last_update_date(self):
    #     return self._last_update_date

    @property
    def devices(self):
        return self.devices

    def get_key(self, device):
        key = str(device.macaddress)
        return key

    def add_device(self, device):
        key = self.get_key(device)
        self.devices[key] = device

    def has_device(self, device):
        key = self.get_key(device)
        return bool(key in self.devices)

    def check_device(self, device):
        if self.has_device(device):
            self.add_device(device)
            return True
        self.add_device(device)
