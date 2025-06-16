import os

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig


def init_config() :
    """
    init config
    """
    parentRoot = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(parentRoot, "config/config.yaml")
    # 2. 初始化配置管理器
    manager = ConfigContainer.get_manager(FullConfig)
    # 3. 从YAML加载配置
    manager.load_from_yaml(config_path)

if __name__ == "__main__":
    init_config()
