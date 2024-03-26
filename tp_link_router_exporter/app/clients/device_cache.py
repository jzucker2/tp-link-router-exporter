from flask import current_app as app


log = app.logger


class DeviceCacheException(Exception):
    pass


class DeviceCacheValue(object):
    def __init__(self, device, update_date):
        super().__init__()
        self.device = device
        self.update_date = update_date

    def __repr__(self):
        return f'DeviceCacheValue ({self.update_date}) => {self.device.ipaddress}'


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
        return device_hash

    def add_or_update_device(self, device, update_date):
        key = self.get_key(device, update_date)
        self.devices[key] = DeviceCacheValue(device, update_date)

    def has_device(self, device, update_date):
        key = self.get_key(device, update_date)
        return bool(key in self.devices)

    @classmethod
    def is_stale(cls, cached_device, update_date):
        log.debug(f'cached_device: {cached_device} => {update_date}')
        return bool(cached_device.update_date < update_date)

    @classmethod
    def is_fresh(cls, cached_device, update_date):
        return not cls.is_stale(cached_device, update_date)

    def get_stale_devices_map(self, update_date):
        log.debug(f'get_stale_devices_map {len(self.devices)}')
        dev_map = {
            k: v for k, v
            in self.devices.items() if self.is_stale(v, update_date)
        }
        log.debug(f'dev_map: {dev_map}')
        return dev_map

    def get_fresh_devices_map(self, update_date):
        log.debug(f'get_fresh_devices_map {len(self.devices)}')
        return {
            k: v for k, v
            in self.devices.items() if self.is_fresh(v, update_date)
        }

    def drop_all_stale_devices(self, update_date):
        log.debug(f'^^^^^^^^^^^^ drop_all_stale_devices '
                  f'starting ({len(self.devices)}) {self.devices}')
        fresh_devices = self.get_fresh_devices_map(update_date)
        log.debug(f'------------ drop_all_stale_devices '
                  f'fresh_devices ({len(fresh_devices)}) {fresh_devices}')
        self._devices = fresh_devices
