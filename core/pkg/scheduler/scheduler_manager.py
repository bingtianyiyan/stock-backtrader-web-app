import asyncio
import functools
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_MISSED
)

from core.pkg.scheduler.config import SchedulerConfig

logger = logging.getLogger(__name__)

#定时任务管理器
class SchedulerManager:
    """
    高级定时任务管理器
    功能特点：
    - 支持内存/SQLite/PostgreSQL/MySQL存储
    - 线程/进程执行器可选
    - 完整的任务生命周期管理
    - 健壮的错误处理和日志记录
    """

    def __init__(self, config: SchedulerConfig):
        """
        初始化调度器
        :param config: 调度器配置
        :raises RuntimeError: 初始化失败时抛出
        """
        self.config = config
        self.logger = self._setup_logger()
        self._scheduler = self._init_scheduler()

    def _setup_logger(self) -> logging.Logger:
        """配置专用日志器"""
        logger = logging.getLogger('apscheduler.manager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _init_scheduler(self) -> BackgroundScheduler:
        """初始化调度器实例"""
        try:
            # 准备存储配置
            jobstores = {
                'default': self._create_jobstore()
            }

            # 准备执行器
            executors = {
                'default': self._create_executor()
            }

            # 合并任务默认配置
            job_defaults = {
                'coalesce': True,
                'max_instances': 3,
                'misfire_grace_time': 60
            }
            job_defaults.update(self.config.job_defaults)

            # 创建调度器
            scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=self.config.timezone,
                daemon=False
            )

            # 添加事件监听
            self._add_event_listeners(scheduler)

            scheduler.start()
            self.logger.info(
                f"Scheduler started with {self.config.jobstore_type} storage "
                f"and {self.config.exec_type} executor"
            )
            return scheduler

        except Exception as e:
            self.logger.critical(f"Scheduler initialization failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Scheduler init failed: {str(e)}") from e

    def _create_jobstore(self):
        """创建作业存储"""
        if self.config.jobstore_type == 'memory':
            return MemoryJobStore()

        common_options = {
            'engine_options': {
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'connect_args': {'connect_timeout': 5}
            }
        }

        if self.config.jobstore_type == 'sqlite':
            return SQLAlchemyJobStore(
                url=self.config.database_url,
                **common_options
            )

        # PostgreSQL/MySQL
        return SQLAlchemyJobStore(
            url=self.config.database_url,
            tablename=f'apscheduler_{self.config.jobstore_type}_jobs',
            **common_options
        )

    def _create_executor(self):
        """创建执行器"""
        if self.config.exec_type == 'thread':
            return ThreadPoolExecutor(
                max_workers=self.config.max_workers,
                #thread_name_prefix='APScheduler'
            )
        return ProcessPoolExecutor(max_workers=self.config.max_workers)

    def _add_event_listeners(self, scheduler: BackgroundScheduler):
        """添加事件监听器"""

        def job_event_listener(event):
            if event.code == EVENT_JOB_ADDED:
                self.logger.debug(f"Job added: {event.job_id}")
            elif event.code == EVENT_JOB_EXECUTED:
                self.logger.debug(f"Job executed: {event.job_id}")
            elif event.code == EVENT_JOB_ERROR:
                self.logger.error(
                    f"Job {event.job_id} failed: {str(event.exception)}",
                    exc_info=event.exception
                )
            elif event.code == EVENT_JOB_MISSED:
                self.logger.warning(f"Job {event.job_id} missed scheduled run")

        scheduler.add_listener(job_event_listener,
                               EVENT_JOB_ADDED | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    def create_cron_trigger(
            self,
            cron_expr: str,
            timezone,
            start_time=None,
            end_time=None
    ):
        """创建Cron触发器（兼容5字段和6字段表达式）"""
        fields = cron_expr.strip().split()

        if len(fields) == 5:
            return CronTrigger.from_crontab(cron_expr, timezone=timezone)
        elif len(fields) == 6:
            return CronTrigger(
                second=fields[0],
                minute=fields[1],
                hour=fields[2],
                day=fields[3],
                month=fields[4],
                day_of_week=fields[5],
                timezone=timezone,
                start_date=start_time,
                end_date=end_time
            )
        else:
            raise ValueError(f"无效的Cron表达式字段数: 得到 {len(fields)} 个字段，需要5或6个字段")

    def add_interval_task(
            self,
            func: Callable,
            interval: Union[int, float, timedelta],
            job_id: str,
            args: Optional[Tuple] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            max_retries: int = 3,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            jitter: Optional[int] = None
    ) -> bool:
        """
        添加间隔任务
        :param func: 要执行的函数
        :param interval: 间隔时间(秒)或timedelta对象
        :param job_id: 任务唯一标识
        :param args: 函数位置参数
        :param kwargs: 函数关键字参数
        :param max_retries: 最大重试次数
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param jitter: 随机延迟秒数
        :return: 是否添加成功
        """
        try:
            seconds = interval.total_seconds() if isinstance(interval, timedelta) else interval
            trigger = IntervalTrigger(
                seconds=seconds,
                start_date=start_time if start_time else datetime.now(self.config.timezone),
                end_date=end_time,
                jitter=jitter
            )
            self._scheduler.add_job(
                func=self._retry_wrapper(func, max_retries),
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=True
            )
            self.logger.info(f"Added interval task [{job_id}] every {seconds} seconds")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add interval task [{job_id}]: {str(e)}")
            return False

    def add_cron_task(
            self,
            func: Callable,
            cron_expr: str,
            job_id: str,
            args: Optional[Tuple] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            max_retries: int = 3,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None
    ) -> bool:
        """
        添加Cron定时任务
        :param cron_expr: Cron表达式 (如 "0 12 * * *")
        :param timezone: 时区 (默认使用配置时区)
        """
        try:
            # 创建trigger时不带start_date/end_date
            trigger = self.create_cron_trigger(
                cron_expr=cron_expr,  # 确保使用关键字参数
                timezone=self.config.timezone,
                start_time=start_time,
                end_time=end_time
            )

            # 在add_job时设置start_date/end_date
            self._scheduler.add_job(
                func=self._retry_wrapper(func, max_retries),
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=True,
                next_run_time=start_time if start_time else datetime.now(self.config.timezone),
                end_date=end_time
            )
            self.logger.info(f"Added cron task [{job_id}] with expression '{cron_expr}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add cron task [{job_id}]: {str(e)}")
            return False

    def remove_task(self, job_id: str) -> bool:
        """删除指定任务"""
        try:
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
                self.logger.info(f"Removed task [{job_id}]")
                return True
            self.logger.warning(f"Task [{job_id}] not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove task [{job_id}]: {str(e)}")
            return False

    def pause_task(self, job_id: str) -> bool:
        """暂停指定任务"""
        try:
            job = self._scheduler.get_job(job_id)
            if not job:
                self.logger.warning(f"Task [{job_id}] not found")
                return False
            if not job.next_run_time:
                self.logger.warning(f"Task [{job_id}] already paused")
                return True

            self._scheduler.pause_job(job_id)
            self.logger.info(f"Paused task [{job_id}]")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pause task [{job_id}]: {str(e)}")
            return False

    def resume_task(self, job_id: str) -> bool:
        """恢复已暂停的任务"""
        try:
            job = self._scheduler.get_job(job_id)
            if not job:
                self.logger.warning(f"Task [{job_id}] not found")
                return False
            if job.next_run_time:
                self.logger.warning(f"Task [{job_id}] already running")
                return True

            self._scheduler.resume_job(job_id)
            self.logger.info(f"Resumed task [{job_id}]")
            return True
        except Exception as e:
            self.logger.error(f"Failed to resume task [{job_id}]: {str(e)}")
            return False

    def get_all_tasks(self) -> Dict[str, Job]:
        """获取所有任务字典 {job_id: Job}"""
        return {job.id: job for job in self._scheduler.get_jobs()}

    def get_task_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务详细信息"""
        job = self._scheduler.get_job(job_id)
        if not job:
            return None
        return {
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time,
            'trigger': str(job.trigger),
            'paused': job.next_run_time is None
        }

    def modify_task_schedule(
            self,
            job_id: str,
            **trigger_kwargs
    ) -> bool:
        """修改任务调度时间"""
        try:
            job = self._scheduler.get_job(job_id)
            if not job:
                self.logger.warning(f"Task [{job_id}] not found")
                return False

            if isinstance(job.trigger, IntervalTrigger):
                new_trigger = IntervalTrigger(**trigger_kwargs)
            elif isinstance(job.trigger, CronTrigger):
                new_trigger = CronTrigger(**trigger_kwargs)
            else:
                raise ValueError(f"Unsupported trigger type: {type(job.trigger)}")

            self._scheduler.reschedule_job(job_id, trigger=new_trigger)
            self.logger.info(f"Rescheduled task [{job_id}]")
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify task [{job_id}]: {str(e)}")
            return False

    def shutdown(self, wait: bool = True) -> None:
        """关闭调度器"""
        try:
            self._scheduler.shutdown(wait=wait)
            self.logger.info("Scheduler stopped gracefully")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
            if not wait:
                self._scheduler.shutdown(wait=False)
            raise

    def _retry_wrapper(self, func: Callable, max_retries: int) -> Callable:
        """错误重试装饰器"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries <= max_retries:
                        self.logger.warning(
                            f"Task failed (attempt {retries}/{max_retries}): {str(e)}"
                        )
                    else:
                        self.logger.error(
                            f"Task failed after {max_retries} attempts: {str(e)}"
                        )
                        raise

        return wrapper

    # 包装器（确保协程被正确执行）
    def sync_wrapper(self,coro_func):
        @functools.wraps(coro_func)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro_func(*args, **kwargs))
            finally:
                loop.close()

        return wrapper

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        if exc_val:
            self.logger.error(
                "Context manager exited with error",
                exc_info=(exc_type, exc_val, exc_tb)
            )




