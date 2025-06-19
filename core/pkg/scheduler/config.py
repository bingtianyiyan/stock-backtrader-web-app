from typing import Optional, Literal, Dict, Any
from datetime import tzinfo
from zoneinfo import ZoneInfo  # Python 3.9+
from pydantic import BaseModel, Field, validator, ConfigDict
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor



#定时任务配置文件
class SchedulerConfig(BaseModel):
    """
    调度器配置实体
    :param jobstore_type: 存储类型 ('memory' | 'sqlite' | 'postgresql' | 'mysql')
    :param database_url: 数据库连接字符串 (jobstore_type不为memory时必填)
    :param max_workers: 线程池大小
    :param exec_type: 执行器类型 ('thread' | 'process')
    :param timezone: 时区设置
    :param job_defaults: 任务默认配置
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)  # 关键配置
    jobstore_type: Literal['memory', 'sqlite', 'postgresql', 'mysql'] = Field('memory', description="存储后端类型")
    database_url: Optional[str] = Field(
        None,
        description="数据库连接URL，格式示例:\n"
                    "sqlite: sqlite:///jobs.db\n"
                    "postgresql: postgresql://user:pass@localhost/db\n"
                    "mysql: mysql+pymysql://user:pass@localhost/db"
    )
    max_workers: int = Field(5, ge=1, le=50, description="最大工作线程数")
    exec_type: Literal['thread', 'process'] = Field('thread', description="执行器类型")
    timezone: tzinfo = Field(default=ZoneInfo("Asia/Shanghai"))
    job_defaults: Dict[str, Any] = Field(
        {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 60
        },
        description="任务默认配置"
    )

    @validator('timezone', pre=True)
    def validate_timezone(cls, v):
        if isinstance(v, str):
            return ZoneInfo(v)
        elif isinstance(v, tzinfo):
            return v
        raise ValueError("时区必须是字符串或 tzinfo 对象")

    @validator('database_url', always=True)
    def validate_database_url(cls, v, values):
        if values.get('jobstore_type') != 'memory' and not v:
            raise ValueError("非内存存储必须提供database_url")
        return v

    @property
    def jobstore_config(self) -> Dict[str, Any]:
        """生成jobstore配置字典"""
        if self.jobstore_type == 'memory':
            return {'default': MemoryJobStore()}

        return {
            'default': SQLAlchemyJobStore(
                url=self.database_url,
                engine_options={
                    'pool_pre_ping': True,
                    'pool_recycle': 3600
                }
            )
        }

    @property
    def executor_config(self) -> Dict[str, Any]:
        """生成executor配置字典"""
        executor_class = ThreadPoolExecutor if self.exec_type == 'thread' else ProcessPoolExecutor
        return {
            'default': executor_class(max_workers=self.max_workers)
        }

    # @property
    # def executors(self):
    #     return {
    #         'default': {
    #             'type': 'asyncio',  # 使用异步执行器
    #             # 或者明确指定类
    #             # 'class': 'apscheduler.executors.asyncio:AsyncIOExecutor'
    #         }
    #     }
