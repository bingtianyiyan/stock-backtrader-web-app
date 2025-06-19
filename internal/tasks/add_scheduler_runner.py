import asyncio
import functools
import logging
from typing import Callable

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.pkg.scheduler.scheduler_manager import SchedulerManager

logger = logging.getLogger(__name__)

async def async_task():
    print("Async task running...")
    await asyncio.sleep(1)
    print("Async task completed")

def midnight_task():
    logger.info("Midnight task")

with SchedulerManager(ConfigContainer.get_config(FullConfig).scheduler_config) as scheduler_manager:

    # 添加Cron任务
    scheduler_manager.add_cron_task(
        func= midnight_task,
        cron_expr="*/5 * * * *",  # 5秒
        job_id="midnight_task2"
    )

    scheduler_manager.add_cron_task(
        func= midnight_task,
        cron_expr="*/5 * * * *",  # 5秒
        job_id="midnight_task3"
    )

    # scheduler_manager.add_cron_task(
    #     func=calculate_top,
    #     cron_expr="*/60 * * * *",
    #     job_id="today_top_task_test"
    # )
    # scheduler_manager.add_cron_task(
    #     func=calculate_shoot_top,
    #     cron_expr="30 9 * * 1-5",
    #     job_id="today_short_task"
    # )
    # scheduler_manager.add_cron_task(
    #     func=record_data_and_build_stock_pools,
    #     cron_expr="0 16 * * 1-5",
    #     job_id="stock_pool_task"
    # )
    # 防止主线程退出
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     scheduler_manager.shutdown()
