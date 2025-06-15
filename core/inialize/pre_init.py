# -*- coding: utf-8 -*-
import importlib
import logging
import os
import pkgutil
import pprint
import shutil
from logging.handlers import RotatingFileHandler
from typing import List

import pandas as pd
import pkg_resources
from omegaconf import OmegaConf

from consts import ZVT_TEST_HOME, ZVT_HOME
from core.config.configmanager import configmanager

__version__ = "1.0.0"  # 手动维护版本

from core.inialize.logger import init_log

logger = logging.getLogger(__name__)

os.environ.setdefault("SQLALCHEMY_WARN_20", "1")
pd.set_option("expand_frame_repr", False)
pd.set_option("mode.chained_assignment", "raise")
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

_plugins = {}

def init_env(zvt_home: str, **kwargs) -> dict:
    """
    init env

    :param zvt_home: home path for zvt
    """
    resource_path = os.path.join(zvt_home, "resources")
    tmp_path = os.path.join(zvt_home, "tmp")
    if not os.path.exists(resource_path):
        os.makedirs(resource_path)

    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    zvt_env = {}
    zvt_env["zvt_home"] = zvt_home
    zvt_env["resource_path"] = resource_path
    zvt_env["tmp_path"] = tmp_path

    # path for storing logs
    zvt_env["log_path"] = os.path.join(zvt_home, "logs")
    if not os.path.exists(zvt_env["log_path"]):
        os.makedirs(zvt_env["log_path"])
    conf_obj = OmegaConf.create(zvt_env)
    configmanager.update_env(OmegaConf.to_object(conf_obj))

    logger = init_log()

    pprint.pprint(zvt_env)

    init_resources(resource_path=resource_path)
    # init config
    init_config()
    # init plugin
    # init_plugins()
    registerMeta()

    logger.info("init config done")
    return zvt_env


def init_resources(resource_path):
    package_name = "core"
    package_dir = pkg_resources.resource_filename(package_name, "resources")
    from core.utils.file_utils import list_all_files

    files: List[str] = list_all_files(package_dir, ext=None)
    for source_file in files:
        dst_file = os.path.join(resource_path, source_file[len(package_dir) + 1 :])
        if not os.path.exists(dst_file):
            shutil.copyfile(source_file, dst_file)


def init_config() -> dict:
    """
    init config
    """

    #根据环境变量读取
    env = ""
    # 2. 加载基础配置 + 环境特定配置
    parentRoot = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(parentRoot, "config/config.yaml")
    base_config = OmegaConf.load(config_path)
    env = base_config.get("current_env")
    if not env:
        env = os.getenv("APP_ENV", "dev")
    config_path = os.path.join(parentRoot, f"config/{env}_config.yaml")
    env_config = OmegaConf.load(config_path)
    # 3. 合并配置（环境配置覆盖基础配置）
    current_config = OmegaConf.merge(base_config, env_config)
    # 解析所有插值并转为普通字典（如果需要）
    #resolved_config = OmegaConf.to_container(current_config, resolve=True)
    configmanager.update(OmegaConf.to_object(current_config))
    return OmegaConf.to_object(current_config)


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

def pre_init():
    print("pre_init")

if os.getenv("TESTING_ZVT"):
    init_env(zvt_home=ZVT_TEST_HOME)

else:
    init_env(zvt_home=ZVT_HOME)


