import sys
from pathlib import Path
from loguru import logger
from typing import Union, Optional, TypeVar


T = TypeVar('T')

class LoguruLogger:
    """
    Loguru 封装的日志组件类

    功能：
    - 多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    - 控制台 + 文件双输出
    - 自动按大小/时间轮转日志文件
    - 异常自动捕获（含堆栈跟踪）
    - 线程安全

    示例：
        >>> log = LoguruLogger("mylog.log")
        >>> log.debug("调试信息")
        >>> log.error("错误", exc_info=True)  # 自动记录异常
    """

    def __init__(
            self,
            log_file: Optional[Union[str, Path]] = None,
            level: str = "INFO",
            rotation: str = "10 MB",
            retention: str = "7 days",
            enqueue: bool = True,
            diagnose: bool = True #正式环境设置为False
    ):
        # 移除默认handler
        logger.remove()

        # 控制台输出
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            enqueue=enqueue,
            diagnose=diagnose
        )

        # 文件输出
        if log_file:
            logger.add(
                str(log_file),
                level=level,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                       "{level: <8} | "
                       "{name}:{function}:{line} - {message}",
                rotation=rotation,
                retention=retention,
                enqueue=enqueue,
                diagnose=diagnose,
                encoding="utf-8"
            )

        self._logger = logger

    def debug(self, message: str, *args, **kwargs):
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, exc_info: bool = False, **kwargs):
        self._logger.error(message, *args, **kwargs)
        if exc_info and sys.exc_info()[0] is not None:
            self._logger.opt(exception=True).error("Exception occurred:")

    def critical(self, message: str, *args, **kwargs):
        self._logger.critical(message, *args, **kwargs)

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

    def bind(self, **kwargs):
        return self._logger.bind(**kwargs)

# logging_config.py
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)

# ---------------------- 使用示例 ----------------------
if __name__ == "__main__":
    # 获取当前文件所在目录的父级父级目录（即项目根目录）
    BASE_DIR = Path(__file__).parent.parent.parent  # 根据实际层级调整
    LOG_DIR = BASE_DIR / "logs"  # 项目根目录下的logs文件夹
    LOG_DIR.mkdir(exist_ok=True)  # 自动创建目录
    # 初始化日志（输出到控制台和文件）
    log = LoguruLogger(
        log_file= LOG_DIR / "app.log",
        level="DEBUG",
        rotation="100 MB",
        retention="30 days"
    )

    # 常规日志
    log.info("服务启动成功")
    log.debug("调试信息：当前用户={}", "admin")


    # 异常捕获（自动记录堆栈）
    @log.catch
    def risky_operation():
        return 1 / 0


    try:
        risky_operation()
    except:
        log.error("操作失败", exc_info=True)

    # 上下文绑定
    task_log = log.bind(task_id="12345")
    task_log.info("任务处理中...")