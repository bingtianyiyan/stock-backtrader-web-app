import sys
from ..base import LogWriter


class ConsoleWriter(LogWriter):
    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def write(self, record):
        print(f"[{record['level']}] {record['message']}", file=self.stream)

    def flush(self):
        self.stream.flush()

    def close(self):
        pass