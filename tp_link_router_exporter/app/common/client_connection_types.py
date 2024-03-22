from enum import Enum


class ClientConnectionTypes(Enum):
    WIFI = 'wifi'
    WIRED = 'wired'
    TOTAL = 'total'

    @property
    def label_string(self):
        return self.value
