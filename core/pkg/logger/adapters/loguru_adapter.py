import json

from loguru import logger

from ..base import BaseLogger
from ..config import LoggerConfig, FileWriterArgs, ConsoleWriterArgs
import sys
from pathlib import Path
from typing import Dict, Any, Optional, TypeVar, Callable
from functools import wraps

from ..options import Options

T = TypeVar('T')


class LoguruAdapter(BaseLogger):
    def __init__(self, config: Options):
        """
               初始化适配器

               参数:
                   config: 如果为None，则使用默认配置
               """
        self._logger = logger
        if config is not None:
            self._setup_handlers(config)

    def _setup_handlers(self, config: Options):
        """配置日志处理器"""
        logger.remove()  # 清除现有处理器
        """配置所有日志处理器"""
        for writer in config.write_to:
            try:
                if writer.name == 'console':
                    self._add_console_handler(writer.args, config.level.upper())
                elif writer.name == 'file':
                    if not writer.args:
                        raise ValueError("File writer requires 'args' section")
                    self._add_file_handler(writer.args,config.level.upper())
            except Exception as e:
                sys.stderr.write(f"Failed to init {writer.name} writer: {str(e)}\n")

    # ---- 标准写入器实现 ----
    def _add_console_handler(self, args: ConsoleWriterArgs, default_level: str):
        """控制台日志（支持颜色/黑白模式）"""
        logger.add(
            sys.stderr,
            level=default_level,
            format=getattr(args, 'format',
                              "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                              "<level>{message}</level> |"
                              "<yellow>{extra}</yellow>"
                              ),
            colorize=getattr(args, 'colorize', True),
            filter=getattr(args, 'filter',None)
        )

    def _add_file_handler(self, args: FileWriterArgs, default_level: str):
        """文件日志（支持轮转/压缩）"""
        Path(args.path).parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            args.path,
            level=default_level,
            rotation=getattr(args, 'max_size', '500 MB'),  # 使用getattr提供默认值
            retention=getattr(args, 'retention', '7 days'),
            compression=getattr(args, 'compression',None),
            format=getattr(args,'format',
                              "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <8}</level> | "
                              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                              "<level>{message}</level> |"
                              "<yellow>{extra}</yellow>"
                              ),
            # serialize=True,  # 关键设置
            # format="{message}",  # 简单消息即可，serialize会处理其他字段
            encoding=getattr(args,'encoding', 'utf-8')
        )

    # ---- 扩展写入器实现 like kafka/es等组件----

    # ---- 核心接口实现 ----
    def log(self, level: str, msg: str, **kwargs):
        logger.log(level, msg, **kwargs)

    def bind(self, **kwargs) -> 'LoguruAdapter':
        """绑定上下文字段"""
        new_adapter = self.__class__.__new__(self.__class__)
        new_adapter._logger = logger.bind(**kwargs)
        return new_adapter

    def add_writer(self, writer_config: Options):
        """动态添加写入器（线程安全）"""
        for writer in writer_config.write_to:
            if writer.name not in _writer_types:
               raise ValueError(f"Unsupported writer type: {writer.name}")
        self._setup_handlers(writer_config)
       # self._setup_handlers(LoggerConfig(writers=[writer_config]))

 # ---- 核心日志方法  ----
    def info(self, message: str, **kwargs):
        """INFO级别日志"""
        if kwargs:
            logger.bind(**kwargs).info(message)
        else:
            logger.info(message)

    def debug(self, message: str, **kwargs):
        """DEBUG级别日志"""
        if kwargs:
            logger.bind(**kwargs).debug(message)
        else:
            logger.debug(message)

    def warn(self, message: str, **kwargs):
        """WARNING级别日志"""
        if kwargs:
            logger.bind(**kwargs).warning(message)
        else:
            logger.warning(message)

    def error(self, message: str, exc_info: Optional[bool] = False, **kwargs):
        """ERROR级别日志（支持异常捕获）"""
        if exc_info:
            kwargs["exc_info"] = True  # 自动记录堆栈跟踪
        if kwargs:
            logger.bind(**kwargs).error(message)
        else:
            logger.error(message)


    # ---- 上下文和异常处理 ----

    def catch(self,
             reraise: bool = False,
             onerror: Optional[Callable[[Exception], Any]] = None,
             default: Optional[T] = None) -> Callable:
        """异常捕获装饰器"""
        @wraps(logger.catch)
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.error(f"Exception in {func.__name__}", exc_info=True)
                    if onerror:
                        onerror(e)
                    if reraise:
                        raise
                    return default
            return wrapper
        return decorator

    # ---- 辅助方法 ----
    def with_fields(self, **kwargs) -> 'LoguruAdapter':
        """链式调用字段绑定（别名）"""
        return self.bind(**kwargs)



# 支持的写入器类型
_writer_types = {
    'console', 'file'
}



