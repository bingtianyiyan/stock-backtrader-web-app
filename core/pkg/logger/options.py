from typing import List, Optional, Callable, Any
from dataclasses import dataclass, field

from core.pkg.logger.config import FileWriterArgs


@dataclass
class WriteTo:
    name: str
    args: Any  # 这里使用Any因为args可以是File或其他类型

@dataclass
class Options:
    driver: str
    level: str
    write_to: List[WriteTo]

Option = Callable[[Options], None]

def set_default() -> Options:
    return Options(
        driver="loguru",
        level="warn",
        write_to=[
            WriteTo(name="file", args=FileWriterArgs(path="temp/logs"))
        ]
    )

def with_driver(s: str) -> Option:
    def wrapper(o: Options):
        o.driver = s
    return wrapper

def with_level(s: str) -> Option:
    def wrapper(o: Options):
        o.level = s
    return wrapper

def with_write_to(s: List[WriteTo]) -> Option:
    def wrapper(o: Options):
        o.write_to = s
    return wrapper