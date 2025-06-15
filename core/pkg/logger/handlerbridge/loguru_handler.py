import logging
from loguru import logger

#创建日志桥接器，兼容原生日志
class LoguruHandler(logging.Handler):
    """将原生logging消息转发到Loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(
            depth=6,  # 调整堆栈深度确保正确文件名
            exception=record.exc_info
        ).log(level, record.getMessage())


def setup_compatible_logging():
    """配置双日志系统"""
    # 1. 移除所有原生处理器
    logging.basicConfig(handlers=[], force=True)

    # 2. 将根日志器指向Loguru
    root_logger = logging.getLogger()
    root_logger.addHandler(LoguruHandler())
    root_logger.setLevel(logging.INFO)  # 设置默认级别

    # 3. 可选：禁用第三方库的冗余日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)