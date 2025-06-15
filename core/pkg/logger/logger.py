import logging
from dataclasses import dataclass
from typing import Optional, List

from core.pkg.logger.adapters.loguru_adapter import LoguruAdapter
from core.pkg.logger.base import BaseLogger
from core.pkg.logger.config import LoggerConfig
from core.pkg.logger.helpers import LogHelper
from core.pkg.logger.options import WriteTo, set_default, with_driver, with_level, with_write_to, Option

# 全局日志变量
Log: Optional[LogHelper] = None

@dataclass
class Logger:
    driver: str
    level: str
    write_to: List[WriteTo]

#如果什么都不配置则初始化一个默认的日志对象，在还未读取配置文件时候作为临时日志对象去处理日志
def new_default_log() -> BaseLogger:
    op = set_default()
    log_config = Logger(
        driver=op.driver,
        level=op.level,
        write_to=op.write_to
    )
    return init_loguru(
        with_driver(log_config.driver),
        with_level(log_config.level),
        with_write_to(log_config.write_to)
    )

#如果是配置了则读取这个对象去处理日志
def new_log(log_config: Logger) -> BaseLogger:
    #如果还有其他日志组件在这边使用driver区分，暂时就一个
    return init_loguru(
        with_driver(log_config.driver),
        with_level(log_config.level),
        with_write_to(log_config.write_to))

#初始化loguru
def init_loguru(*opts: Option) -> BaseLogger:
    op = set_default()
    for o in opts:
        o(op)

    # # 配置日志级别
    # level = op.level.upper()
    # # 自定义配置
    # config = LoggerConfig(
    #     level=level,
    #     writers= op.write_to
    # )
    logger = LoguruAdapter(op)

    # 创建日志助手
    global Log
    Log = logger
    return Log

# def create_logger(config=None) -> BaseLogger:
#     """工厂函数创建日志实例"""
#     config = config or LoggerConfig()
#     return LoguruAdapter(config)
