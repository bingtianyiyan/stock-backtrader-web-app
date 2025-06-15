import os

from omegaconf import OmegaConf

from core.config.configmanager import configmanager


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

