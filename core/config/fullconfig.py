from typing import Generic, TypeVar, Optional, Dict, Any, List
from pydantic import BaseModel, validator, Field

from core.config.config_models import JQDataConfig, ProxyConfig, EmailConfig, WeChatConfig, QMTConfig, AIConfig, SqlInfo
from core.pkg.logger.config import LoggerConfig

# 泛型类型，用于扩展不同模块的配置
T = TypeVar('T')

class DatabaseConfig(BaseModel, Generic[T]):
    host: str= "localhost"
    port: int = Field(gt=0, le=65535)  # 端口校验
    username: Optional[str] = None  # 改为可选字段
    password: Optional[str] = None
    database: Optional[str] = None
    extra: Optional[T] = None


class AppConfig(BaseModel):
    debug: bool = False
    env: str = "prod" # dev,stage,prod

class MySQLExtraConfig(BaseModel):
    pool_size: int = 5
    charset: str = "utf8mb4"
    connect_timeout: int = 10

# 将泛型具体化为 MySQL 配置
MySQLConfig = DatabaseConfig[MySQLExtraConfig]


#所有配置文件集合
class FullConfig(BaseModel):
    app: AppConfig
    mainConn: MySQLConfig
    jobConn: MySQLConfig
    logger: LoggerConfig
    """聚合所有配置的顶级模型"""
    jqdata: JQDataConfig = Field(default_factory=JQDataConfig)
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    wechat: WeChatConfig = Field(default_factory=WeChatConfig)
    qmt: QMTConfig = Field(default_factory=QMTConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    sqlinfo: SqlInfo = Field(default_factory=SqlInfo)