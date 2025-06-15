# -*- coding: utf-8 -*-
import importlib
import logging
import os
import pkgutil
import shutil
from typing import List

import pandas as pd
import pkg_resources


__version__ = "1.0.0"  # 手动维护版本

from omegaconf import OmegaConf

from core.config.configmanager import configmanager
from core.inialize.config import init_config

from core.inialize.logger import init_log
from core.inialize.resources import init_resources

logger = logging.getLogger(__name__)

os.environ.setdefault("SQLALCHEMY_WARN_20", "1")
pd.set_option("expand_frame_repr", False)
pd.set_option("mode.chained_assignment", "raise")
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

_plugins = {}

def init_env():
    """
    init env

    :param zvt_home: home path for zvt
    """

    # init config
    init_config()
    # init log
    init_log()

    init_resources()

    # init plugin
    # init_plugins()
    #registerMeta()

    logger.info("init config done")



def init_plugins():
    for finder, name, ispkg in pkgutil.iter_modules():
        if name.startswith("tiny_"):
            try:
                _plugins[name] = importlib.import_module(name)
            except Exception as e:
                logger.warning(f"failed to load plugin {name}", e)
    logger.info(f"loaded plugins:{_plugins}")


# register to meta

import platform

def registerMeta():
    if platform.system() == "Windows":
        try:
            import core.recorders.qmt as qmt_recorder
        except Exception as e:
            logger.error("QMT not work", e)
    else:
        logger.warning("QMT need run in Windows!")

#先初始化config信息
init_env()


