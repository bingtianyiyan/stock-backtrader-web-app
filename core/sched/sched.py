import logging

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.db.databasemanager import DatabaseManager
from core.db.mysqlx import mysqlconfig

logger = logging.getLogger(__name__)
#TODO 改造定时任务
# configs = ConfigContainer.get_config(FullConfig).db_configs
# # 根据dbname筛选出配置
# if not configs:
#     raise ValueError("db_configs should provider")
# config = next(filter(lambda x: x.db_action == "jobConn", configs), None)
# db_engine = DatabaseManager.get_engine("jobs", config.database, config)
# jobConfig =   ConfigContainer.get_config(FullConfig).jobConn
# config = (mysqlconfig().builder()
#           .with_host(jobConfig.host)
#           .with_port(jobConfig.port)
#           .with_credentials(jobConfig.username, jobConfig.password    )
#           .with_database(jobConfig.database)
#           .with_table_name('zvt_scheduled_jobs')
#           .build())
#
# # 使用MySQL作为作业存储
# jobstores = {
#     "default": SQLAlchemyJobStore(
#         url= config.get_connection_url(),
#         engine_options={
#             "pool_size": 10,
#             "max_overflow": 20,
#             "pool_recycle": 3600,
#             "connect_args": {
#                 "charset": "utf8mb4"
#             }
#         }
#     )
# }
#
# executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
# job_defaults = {"coalesce": False, "max_instances": 1}
#
# zvt_scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
#
#
# def sched_tasks():
#     print()
#     # import platform
#     #
#     # if platform.system() == "Windows":
#     #     try:
#     #         from core.broker.qmt.qmt_quote import record_tick
#     #
#     #         zvt_scheduler.add_job(func=record_tick, trigger="cron", hour=9, minute=19, day_of_week="mon-fri")
#     #     except Exception as e:
#     #         logger.error("QMT not work", e)
#     # else:
#     #     logger.warning("QMT need run in Windows!")
#     #
#     # zvt_scheduler.start()
#
#
# if __name__ == "__main__":
#     sched_tasks()