from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union


@dataclass
class BaseWriterArgs:
    """所有Writer参数的基类"""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@dataclass
class ConsoleWriterArgs(BaseWriterArgs):
    filter: Optional[Callable[[dict], bool]] = None  # 日志过滤函数
    format: Optional[str] = None  # 自定义格式字符串
    colorize: Optional[bool] = True  # 是否启用颜色

#文件日志参数
@dataclass
class FileWriterArgs(BaseWriterArgs):
    path: str = "logs/app_{time:YYYY-MM-DD}.log"
    backup_count: int = 10,
    enqueue = True,
    rotation :Optional[str] = "500 MB"
    retention: Optional[str] = "30 days"  # 日志保留时间
    compression: Optional[str] = None  # 压缩格式，如 'gz'
    encoding: Optional[str] = "utf-8"  # 文件编码


@dataclass
class WriteTo:
    name: str
    args: Optional[Union[ConsoleWriterArgs, FileWriterArgs, Dict[str, Any]]] = None  # 这里使用Any因为args可以是File或其他类型

    def __post_init__(self):
        if isinstance(self.args, dict):
            # 自动转换为对应的Args类
            if self.name == "console":
                self.args = ConsoleWriterArgs(**self.args)
            elif self.name == "file":
                self.args = FileWriterArgs(**self.args)


@dataclass
class Options:
    driver: str
    level: str
    write_to: List[WriteTo]


Option = Callable[[Options], None]


def set_default() -> Options:
    return Options(
        driver="loguru",
        level="info",
        write_to=[
            WriteTo(name="console", args=None)
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


@dataclass
class LoggerConfig:
    """日志配置，复用Options的字段定义"""
    driver: str = "loguru"
    level: str = "info"
    write_to: List[WriteTo] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, cfg: any) -> 'LoggerConfig':
        """从YAML加载配置并自动转换类型"""
       # cfg = OmegaConf.load(config_path).logger
        return cls(
            driver=cfg.get("driver","loguru"),
            level=cfg.get("level","info"),
            write_to=[WriteTo(name=w.get("name"), args=dict(w.get("args", {}))) for w in cfg.get("write_to", [])]
        )

    def get_writer_args(self, writer_name: str) -> Optional[BaseWriterArgs]:
        """获取特定writer的参数（类型安全）"""
        for writer in self.write_to:
            if writer.name == writer_name:
                return writer.args
        return None

    def to_options(self) -> Options:
        """转换为Options对象"""
        return Options(
            driver=self.driver,
            level=self.level,
            write_to=self.write_to
        )

