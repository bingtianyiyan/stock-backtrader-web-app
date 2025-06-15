import gzip
from logging.handlers import RotatingFileHandler
from ..base import LogWriter


class FileWriter(LogWriter):
    def __init__(self, path: str, max_size: int = 500, backup_count: int = 10):
        self.handler = RotatingFileHandler(
            filename=path,
            maxBytes=max_size * 1024 * 1024,
            backupCount=backup_count
        )

    def write(self, record):
        self.handler.emit(record)

    def flush(self):
        self.handler.flush()

    def close(self):
        self.handler.close()