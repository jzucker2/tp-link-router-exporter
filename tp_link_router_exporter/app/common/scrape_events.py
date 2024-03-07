from enum import Enum


class ScrapeEvents(Enum):
    ATTEMPT = 'attempt'
    SUCCESS = 'success'
    ERROR = 'error'
