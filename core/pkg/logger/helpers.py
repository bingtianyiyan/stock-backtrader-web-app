from typing import Dict, Any
from .base import BaseLogger


class LogHelper:
    def __init__(self, logger: BaseLogger, fields: Dict[str, Any] = None):
        self.logger = logger
        self.fields = fields or {}

    def with_fields(self, fields: Dict[str, Any]) -> 'LogHelper':
        return LogHelper(self.logger, {**self.fields, **fields})

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg,  **kwargs)

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)

    def warn(self, msg: str, **kwargs):
        self.logger.warn(msg, **kwargs)

    def error(self, msg: str, exc_info: bool = False, **kwargs):
        self.logger.error(msg, exc_info, **kwargs)
