from enum import Enum


class PacketActions(Enum):
    SENT = 'sent'
    RECEIVED = 'received'

    @property
    def label_string(self):
        return self.value

    @classmethod
    def metrics_actions_list(cls):
        return list([
            cls.RECEIVED,
            cls.SENT,
        ])
