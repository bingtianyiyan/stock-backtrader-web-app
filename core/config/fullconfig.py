from typing import Generic, TypeVar, Optional, Dict, Any, List, Literal
from pydantic import BaseModel, validator, Field

from core.config.config_models import JQDataConfig, ProxyConfig, EmailConfig, WeChatConfig, QMTConfig, AIConfig, SqlInfo
from core.pkg.logger.config import LoggerConfig

# 泛型类型，用于扩展不同模块的配置
T = TypeVar('T')

class DatabaseExtraConfig(BaseModel):
    """数据库额外配置"""
    pool_size: int = Field(5, gt=0, description="连接池大小")
    charset: str = Field("utf8mb4", description="字符编码")
    connect_timeout: Optional[int] = Field(None, description="连接超时(秒)")
    max_overflow: int = Field(20, gt=0, description="最大溢出连接数")
    pool_recycle: int = Field(1800, gt=0, description="连接回收时间（秒）")
    echo: bool = False

class MySQLConfig(BaseModel):
    """MySQL专用配置"""
    ssl_mode: Optional[str] = Field(None, description="SSL模式")
    # 可以添加其他MySQL特有配置

class PostgreSQLConfig(BaseModel):
    """PostgreSQL专用配置"""
    schema_: Optional[str] = Field("public", alias="schema", description="模式名称")
    sslmode: Optional[str] = Field("prefer", description="SSL模式")

class DatabaseConfig(BaseModel):
    """数据库基础配置"""
    db_type: Literal["mysql", "postgresql"]
    db_action: str = Field(..., description="连接用途描述，如mainConn/jobConn")
    host: str= "localhost"
    port: int = Field(gt=0, le=65535)  # 端口校验
    username: Optional[str] = None  # 改为可选字段
    password: Optional[str] = None
    database: Optional[str] = None
    extra: DatabaseExtraConfig = Field(default_factory=DatabaseExtraConfig)
    # 数据库类型特定配置
    mysql_config: Optional[MySQLConfig] = None
    pg_config: Optional[PostgreSQLConfig] = None


class AppConfig(BaseModel):
    debug: bool = False
    env: str = "prod" # dev,stage,prod


#所有配置文件集合
class FullConfig(BaseModel):
    app: AppConfig
    db_configs: List[DatabaseConfig] = Field(..., description="数据库配置列表")
    logger: LoggerConfig
    """聚合所有配置的顶级模型"""
    jqdata: JQDataConfig = Field(default_factory=JQDataConfig)
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    wechat: WeChatConfig = Field(default_factory=WeChatConfig)
    qmt: QMTConfig = Field(default_factory=QMTConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    sqlinfo: SqlInfo = Field(default_factory=SqlInfo)