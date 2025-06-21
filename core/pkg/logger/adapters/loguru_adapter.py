
from loguru import logger
from ..base import BaseLogger
from ..config import FileWriterArgs, ConsoleWriterArgs, LoggerConfig
import sys
from pathlib import Path
from typing import Optional, TypeVar

from ..handlerbridge.loguru_handler import setup_compatible_logging
from ..level import get_level

# 在模块顶部定义默认格式
DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{thread.name}</cyan> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<cyan>{function}</cyan> |"
    "<level>{message}</level> |"
    "<yellow>{extra}</yellow>"
)

class LoguruAdapter(BaseLogger):
    def __init__(self, config: LoggerConfig):
        """
               初始化适配器

               参数:
                   config: 如果为None，则使用默认配置
               """
        self._logger = logger
        if config is not None:
            self._setup_handlers(config)
            #原生桥接日志 初始化（只需一次）
            setup_compatible_logging()

    def _setup_handlers(self, config: LoggerConfig):
        """配置日志处理器"""
        logger.remove()  # 清除现有处理器
        # 转换level
        levelname = get_level(config.level)
        """配置所有日志处理器"""
        for writer in config.write_to:
            try:
                if writer.name == 'console':
                    self._add_console_handler(writer.args, levelname)
                elif writer.name == 'file':
                    if not writer.args:
                        raise ValueError("File writer requires 'args' section")
                    self._add_file_handler(writer.args,levelname)
            except Exception as e:
                sys.stderr.write(f"Failed to init {writer.name} writer: {str(e)}\n")

    # ---- 标准写入器实现 ----
    def _add_console_handler(self, args: Optional[ConsoleWriterArgs], default_level: str):
        """控制台日志（支持颜色/黑白模式）"""
        args = args or ConsoleWriterArgs()
        format = args.format if hasattr(args, 'format') and args.format is not None else DEFAULT_FORMAT
        logger.add(
            sys.stderr,
            level=default_level,
            format=format,
            colorize=getattr(args, 'colorize', True),
            filter=getattr(args, 'filter',None)
        )

    def _add_file_handler(self, args: FileWriterArgs, default_level: str):
        """文件日志（支持轮转/压缩）"""
        Path(args.path).parent.mkdir(parents=True, exist_ok=True)
        #logger.remove()  # 清理旧配置
        logger.add(
            args.path,
            level=default_level,
            rotation=getattr(args, 'rotation', '500 MB'),  # 使用getattr提供默认值
            retention=getattr(args, 'retention', '7 days'),
            compression=getattr(args, 'compression',None),
            mode="a",
            filter= lambda _: True,  # 禁用内部重命名逻辑
            enqueue=getattr(args, 'enqueue', True),
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

    def add_writer(self, writer_config: LoggerConfig):
        """动态添加写入器（线程安全）"""
        for writer in writer_config.write_to:
            if writer.name not in _writer_types:
               raise ValueError(f"Unsupported writer type: {writer.name}")
        self._setup_handlers(writer_config)

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


    def critical(self, message: str, exc_info: Optional[bool] = False, **kwargs):
        """CRITICAL级别日志（支持异常捕获）"""
        if exc_info:
            kwargs["exc_info"] = True  # 自动记录堆栈跟踪
        if kwargs:
            logger.bind(**kwargs).error(message)
        else:
            logger.error(message)

    # ---- 上下文和异常处理 ----
    @property
    def catch(self):
        """
        正确实现的catch装饰器属性
        使用方式：
            @log.catch
            def func(): ...

            或带参数：
            @log.catch(reraise=True)
            def func(): ...
        """
        return self._logger.catch

    # ---- 辅助方法 ----
    def with_fields(self, **kwargs) -> 'LoguruAdapter':
        """链式调用字段绑定（别名）"""
        return self.bind(**kwargs)



# 支持的写入器类型
_writer_types = {
    'console', 'file'
}



