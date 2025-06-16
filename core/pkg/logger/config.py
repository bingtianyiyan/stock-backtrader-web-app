
from typing import List, Dict, Any, Optional, Callable, Union

from pydantic import BaseModel, validator


class ConsoleWriterArgs(BaseModel):
    filter: Optional[Callable[[dict], bool]] = None  # 日志过滤函数
    format: Optional[str] = None  # 自定义格式字符串
    colorize: Optional[bool] = True  # 是否启用颜色

#文件日志参数
class FileWriterArgs(BaseModel):
    path: str = "logs/app_{time:YYYY-MM-DD}.log"
    backup_count:Optional[int] = 10,
    enqueue :Optional[bool] = True,
    rotation :Optional[str] = "500 MB"
    retention: Optional[str] = "30 days"  # 日志保留时间
    compression: Optional[str] = None  # 压缩格式，如 'gz'
    encoding: Optional[str] = "utf-8"  # 文件编码


class WriteTo(BaseModel):
    name: str # "console" 或 "file"
    args: Optional[Union[ConsoleWriterArgs, FileWriterArgs, Dict[str, Any]]] = None  # 这里使用Any因为args可以是File或其他类型

    # 根据 name 自动校验 args 类型
    @validator('args', always=True)
    def validate_args(cls, v, values):
        if 'name' not in values:
            raise ValueError("Missing target name")

        if v is None:
            return None

        if values['name'] == "console" and not isinstance(v, ConsoleWriterArgs):
            return ConsoleWriterArgs(**v) if v else None
        elif values['name'] == "file" and not isinstance(v, FileWriterArgs):
            return FileWriterArgs(**v) if v else None
        return v


class LoggerConfig(BaseModel):
    """日志配置，复用Options的字段定义"""
    driver: str = "loguru"
    level: str = "info"
    write_to: List[WriteTo]


def set_default() -> LoggerConfig:
    return LoggerConfig(
        driver="loguru",
        level="info",
        write_to=[
            WriteTo(name="console", args=None)
        ]
    )

