from flask import current_app as app


log = app.logger


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

    def __repr__(self):
        return f'DeviceCache ({len(self.devices)})'

    @classmethod
    def default_device_cache(cls):
        return cls()

    @classmethod
    def get_date_hash_string(cls, input_dt):
        return input_dt.strftime(cls.DATE_HASH_STRING_FORMAT)

    @property
    def devices(self):
        return self._devices

    def get_key(self, device, update_date):
        device_hash = str(device.macaddress)
        update_hash = self.get_date_hash_string(update_date)
        key = f'{device_hash}=={update_hash}'
        return key

    def add_or_update_device(self, device, update_date):
        key = self.get_key(device, update_date)
        self.devices[key] = DeviceCacheValue(device, update_date)

    def get_device(self, device, update_date):
        key = self.get_key(device, update_date)
        return self.devices[key]

    def has_device(self, device, update_date):
        key = self.get_key(device, update_date)
        return bool(key in self.devices)

    @classmethod
    def is_stale(cls, cached_device, update_date):
        return bool(cached_device.update_date < update_date)

    @classmethod
    def is_fresh(cls, cached_device, update_date):
        return not cls.is_stale(cached_device, update_date)

    def get_stale_devices(self, update_date):
        return {
            k: v for k, v
            in self.devices.items() if self.is_stale(v, update_date)
        }

    def get_fresh_devices_map(self, update_date):
        return {
            k: v for k, v
            in self.devices.items() if self.is_fresh(v, update_date)
        }

    def drop_all_stale_devices(self, update_date):
        fresh_devices = self.get_fresh_devices_map(update_date)
        self._devices = fresh_devices
