from core.config.configmanager import configmanager
from core.pkg.logger.config import LoggerConfig
from core.pkg.logger.logger import new_log

def init_log():
    logconfig = configmanager.get().get("logger")
    conf = LoggerConfig.from_yaml(logconfig)
    # 初始化日志
    new_log(conf)


