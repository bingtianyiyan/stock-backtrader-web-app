import logging
from enum import Enum


class Level(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"

def get_level(level_str: str) -> int:
    level_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "fatal": logging.CRITICAL
    }
    return level_mapping.get(level_str.lower(), logging.WARNING)