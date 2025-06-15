from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import os

@dataclass
class ConsoleWriterArgs:
    filter: Optional[Callable[[dict], bool]] = None  # 日志过滤函数
    format: Optional[str] = None  # 自定义格式字符串
    colorize: Optional[bool] = True  # 是否启用颜色

#文件日志参数
@dataclass
class FileWriterArgs:
    path: str = "logs/app.log"
    max_size: int = 500  # MB
    backup_count: int = 10,
    retention: Optional[str] = "30 days"  # 日志保留时间
    compression: Optional[str] = None  # 压缩格式，如 'gz'
    encoding: Optional[str] = "utf-8"  # 文件编码


@dataclass
class LoggerConfig:
    level: str = "INFO"
    writers: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"name": "console"},
        {"name": "file", "args": FileWriterArgs().__dict__}
    ])

    @classmethod
    def from_env(cls):
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO")
        )