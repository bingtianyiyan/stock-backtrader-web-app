from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import os

from core.pkg.logger.options import Options, WriteTo


@dataclass
class ConsoleWriterArgs:
    filter: Optional[Callable[[dict], bool]] = None  # 日志过滤函数
    format: Optional[str] = None  # 自定义格式字符串
    colorize: Optional[bool] = True  # 是否启用颜色

#文件日志参数
@dataclass
class FileWriterArgs:
    path: str = "logs/app_{time:YYYY-MM-DD}.log"
    backup_count: int = 10,
    enqueue = True,
    rotation :Optional[str] = "500 MB"
    retention: Optional[str] = "30 days"  # 日志保留时间
    compression: Optional[str] = None  # 压缩格式，如 'gz'
    encoding: Optional[str] = "utf-8"  # 文件编码


@dataclass
class LoggerConfig(Options):
    """日志配置，复用Options的字段定义"""
    # level: str
    # write_to: List[WriteTo]
    # driver: str # 添加driver字段以完全匹配Options

    # @classmethod
    # def from_env(cls) -> 'LoggerConfig':
    #     """从环境变量创建配置"""
    #     return cls(
    #         level=os.getenv("LOG_LEVEL", "INFO"),
    #         # 可以添加其他环境变量配置
    #     )

    def to_options(self) -> Options:
        """转换为Options对象"""
        return Options(
            driver=self.driver,
            level=self.level,
            write_to=self.write_to
        )