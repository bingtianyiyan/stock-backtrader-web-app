#其他配置

from typing import Optional
from pydantic import BaseModel, Field, validator

class ProxyConfig(BaseModel):
    """HTTP/HTTPS代理配置"""
    http_proxy: Optional[str] = Field(
        "127.0.0.1:1087",
        description="HTTP代理地址 (格式: ip:port)"
    )
    https_proxy: Optional[str] = Field(
        "127.0.0.1:1087",
        description="HTTPS代理地址 (格式: ip:port)"
    )

    @validator('http_proxy', 'https_proxy')
    def validate_proxy(cls, v):
        if v and ":" not in v:
            raise ValueError("Proxy address must be in format 'host:port'")
        return v

class EmailConfig(BaseModel):
    """邮件服务配置"""
    smtp_host: str = Field(
        "smtpdm.aliyun.com",
        description="SMTP服务器地址"
    )
    smtp_port: int = Field(
        80,
        description="SMTP端口号",
        gt=0, le=65535
    )
    email_username: str = Field(
        "",
        description="邮箱登录用户名"
    )
    email_password: str = Field(
        "",
        description="邮箱登录密码"
    )

class WeChatConfig(BaseModel):
    """微信相关配置"""
    wechat_app_id: str = Field(
        "",
        description="微信公众号APP ID"
    )
    wechat_app_secrect: str = Field(
        "",
        description="微信公众号APP SECRET"
    )
    qiye_wechat_bot_token: str = Field(
        "",
        description="企业微信机器人Token"
    )

class QMTConfig(BaseModel):
    """QMT交易终端配置"""
    qmt_mini_data_path: str = Field(
        "E:\\qmt\\userdata_mini",
        description="QMT迷你版数据路径"
    )
    qmt_account_id: str = Field(
        "",
        description="QMT账户ID"
    )

class AIConfig(BaseModel):
    """AI服务配置"""
    moonshot_api_key: str = Field(
        "",
        description="Moonshot AI API Key"
    )
    qwen_api_key: str = Field(
        "",
        description="阿里通义千问API Key"
    )

class JQDataConfig(BaseModel):
    """聚宽数据配置"""
    jq_username: str = Field(
        "",
        description="聚宽账号用户名"
    )
    jq_password: str = Field(
        "",
        description="聚宽账号密码"
    )

class SqlInfo(BaseModel):
    """日志配置"""
    sqllog: bool = Field(
        False,
        description="是否启用SQL日志"
    )
    initTable: bool = Field(
        False,
        description="是否启用生成表"
    )
