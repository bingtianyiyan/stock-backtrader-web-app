import os
from threading import Lock
from typing import TypeVar, Generic, Optional, Dict, Type, Any

import yaml
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class configmanager(Generic[T]):
    """
      泛型配置管理器，支持类型安全的配置加载和环境变量管理
      用法示例：
          class AppConfig(BaseModel): ...
          manager = ConfigManager[AppConfig]()
      """
    """
    线程安全的泛型配置管理器（内部类）
    """
    _lock = Lock()
    _config: Optional[T] = None
    _env: Dict[str, str] = {}
    _config_type: Type[T]

    def __init__(self, config_type: Type[T]):
        self._config_type = config_type

    def update(self, new_config: Dict[str, Any]) -> None:
        """更新配置字典并验证"""
        with self._lock:
            if self._config is None:
                self._config = self._config_type(**new_config)
            else:
                self._config = self._config.copy(update=new_config)

    def get(self) -> T:
        """获取当前配置(返回副本)"""
        if self._config is None:
            raise ValueError("Configuration not initialized")
        return self._config.copy()

    def update_env(self, new_env: Dict[str, str]) -> None:
        """更新环境变量(同时更新os.environ)"""
        with self._lock:
            self._env.update(new_env)
            os.environ.update(new_env)

    def get_env(self, key: str, default: Optional[str] = None) -> str:
        """获取环境变量"""
        return self._env.get(key, os.getenv(key, default))

    def load_from_yaml(self, file_path: str) -> None:
        """从YAML文件加载配置"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        self.update(data)

    def reload_with_env(self) -> None:
        """用环境变量重新加载配置"""
        if self._config:
            env_vars = {k.lower(): v for k, v in os.environ.items()}
            self.update(env_vars)


# 全局单例容器
class ConfigContainer:
    """全局配置容器（单例模式）"""
    _instance = None
    _managers: Dict[Type[BaseModel], configmanager] = {}
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_manager(cls, config_type: Type[T]) -> configmanager[T]:
        with cls._lock:
            if config_type not in cls._managers:
                cls._managers[config_type] = configmanager(config_type)
            return cls._managers[config_type]

    @classmethod
    def set_config(cls, config_type: Type[T], config_data: Dict[str, Any]) -> None:
        """
        设置或更新配置
        :param config_type: 配置模型类
        :param config_data: 配置字典数据
        """
        cls.get_manager(config_type).update(config_data)

    @classmethod
    def get_config(cls, config_type: Type[T]) -> T:
        """
        获取配置
        :param config_type: 配置模型类
        :return: 配置实例（副本）
        """
        return cls.get_manager(config_type).get()


    @classmethod
    def set_env(cls, new_env: Dict[str, str]) -> None:
        """
        更新环境变量（全局生效）
        :param new_env: 环境变量字典
        """
        next(iter(cls._managers.values())).update_env(new_env)


    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None) -> str:
       return next(iter(cls._managers.values())).get_env(key,default)



# # 快捷访问函数
# def set_config(new_config: Dict[str, Any]) -> T:
#     """获取全局配置(类型安全)"""
#     if not ConfigContainer._managers:
#         raise RuntimeError("No config manager initialized")
#     return ConfigContainer.get_manager().get()
#
# def get_config(config_type: Type[T]) -> T:
#     """获取全局配置(类型安全)"""
#     if not ConfigContainer._managers:
#         raise RuntimeError("No config manager initialized")
#     return ConfigContainer.get_manager(config_type).get()
#
# def get_env(key: str, default: Optional[str] = None) -> str:
#     """
#     获取全局环境变量
#     注意：需要至少初始化一个管理器后才能使用
#     """
#     if not ConfigContainer._managers:
#         raise RuntimeError("No config manager initialized")
#     return next(iter(ConfigContainer._managers.values())).get_env(key, default)
#
#
# def update_env(new_env: Dict[str, str]) -> None:
#     if not ConfigContainer._managers:
#         raise RuntimeError("No config manager initialized")
#     """全局更新环境变量"""
#     next(iter(ConfigContainer._managers.values())).update_env(new_env)
# # 更新环境变量
# manager.update_env({
#     "APP_DEBUG": "true",
#     "LOG_LEVEL": "DEBUG"
# })
#
# # 环境变量覆盖配置
# manager.reload_with_env()