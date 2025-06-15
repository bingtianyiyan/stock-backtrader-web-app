from dataclasses import dataclass
from typing import Optional, List

from core.pkg.logger.adapters.loguru_adapter import LoguruAdapter
from core.pkg.logger.base import BaseLogger
from core.pkg.logger.config import LoggerConfig
from core.pkg.logger.helpers import LogHelper
from core.pkg.logger.options import WriteTo, set_default, with_driver, with_level, with_write_to, Option

# 全局日志变量
Log: Optional[LogHelper] = None


#如果什么都不配置则初始化一个默认的日志对象，在还未读取配置文件时候作为临时日志对象去处理日志
def new_default_log() -> BaseLogger:
    op = set_default()
    log_config = LoggerConfig(
        driver=op.driver,
        level=op.level,
        write_to=op.write_to
    )
    return init_loguru(log_config)

#如果是配置了则读取这个对象去处理日志
def new_log(log_config: LoggerConfig) -> BaseLogger:
    #如果还有其他日志组件在这边使用driver区分，暂时就一个
    return init_loguru(log_config)

#初始化loguru
def init_loguru(log_config: LoggerConfig) -> BaseLogger:
    # 创建日志
    global Log
    Log = LoguruAdapter(log_config)
    return Log

# def create_logger(config=None) -> BaseLogger:
#     """工厂函数创建日志实例"""
#     config = config or LoggerConfig()
#     return LoguruAdapter(config)
