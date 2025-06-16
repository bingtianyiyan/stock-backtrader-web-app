from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.pkg.logger.logger import new_log

def init_log():
    # 获取类型安全的配置
    config = ConfigContainer.get_config(FullConfig)
    # 初始化日志
    new_log(config.logger)


