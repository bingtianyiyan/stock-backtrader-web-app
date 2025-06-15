from abc import ABC, abstractmethod
from typing import Dict, Any
import threading

#日志基础写入组件抽象类
class LogWriter(ABC):
    """日志写入器抽象基类"""

    def __init__(self):
        self._lock = threading.Lock()

    @abstractmethod
    def write(self, record: Dict[str, Any]):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def close(self):
        pass


class BaseLogger(ABC):
    """日志系统抽象基类"""

    @abstractmethod
    def log(self, level: str, msg: str, **kwargs):
        pass

    @abstractmethod
    def bind(self, **kwargs) -> 'BaseLogger':
        pass

    @abstractmethod
    def add_writer(self, writer: LogWriter):
        pass

    # 快捷方法
    def info(self, msg: str, **kwargs):
        self.log('INFO', msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        self.log('DEBUG', msg, **kwargs)

    def warn(self, msg: str, **kwargs):
        self.log('WARN', msg, **kwargs)

    def error(self, msg: str, exc_info: bool = False, **kwargs):
        self.log('ERROR', msg, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, exc_info: bool = False,  **kwargs):
        self.log('CRITICAL', msg, exc_info=exc_info, **kwargs)