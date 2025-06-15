import sys
from pathlib import Path

from core.config.configmanager import configmanager
from core.utils.logs_utils import LoguruLogger


def init_log(file_name="tiny.log", log_dir=None, simple_formatter=True):
    """
    使用 LoguruLogger 改造后的日志初始化
    参数：
        file_name: 日志文件名
        log_dir: 日志目录（默认从配置读取）
        simple_formatter: 是否使用简单格式
    """
    # 获取日志目录
    if not log_dir:
        log_dir = configmanager.get_env().get("log_path")

    # 确保目录存在
    log_path = Path(log_dir) / file_name
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 定义日志格式
    if simple_formatter:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{thread.name}</cyan> | "
            "<level>{message}</level>"
        )
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{thread.name} | "
            "{message}"
        )
    else:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{thread.name}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{file}</cyan>:<cyan>{line}</cyan> | "
            "<cyan>{function}</cyan> | "
            "<level>{message}</level>"
        )
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{thread.name} | "
            "{name}:{file}:{line} | "
            "{function} | "
            "{message}"
        )

    # 初始化 LoguruLogger
    log = LoguruLogger(
        log_file=log_path,
        level="INFO",
        rotation="500 MB",  # 对应原 maxBytes=524288000
        retention="10 days",  # 对应原 backupCount=10
        enqueue=True  # 线程安全
    )

    # 应用自定义格式
    log._logger.remove()  # 移除默认handler

    # 控制台输出
    log._logger.add(
        sys.stderr,
        format=console_format,
        level="INFO",
        enqueue=True
    )

    # 文件输出
    log._logger.add(
        str(log_path),
        format=file_format,
        level="INFO",
        rotation="500 MB",
        retention="10 days",
        enqueue=True,
        encoding="utf-8"
    )

    return log
