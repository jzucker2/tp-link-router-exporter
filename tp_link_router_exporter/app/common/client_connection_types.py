from enum import Enum


class ClientConnectionTypes(Enum):
    WIFI = 'wifi'
    WIRED = 'wired'
    GUEST = 'guest'
    TOTAL = 'total'

    @property
    def label_string(self):
        return self.value

    @classmethod
    def metrics_types_list(cls):
        return list([
            cls.WIFI,
            cls.WIRED,
            cls.GUEST,
            cls.TOTAL,
        ])
