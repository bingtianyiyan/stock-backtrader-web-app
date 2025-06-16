import logging

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.db.mysqlx import mysqlconfig

logger = logging.getLogger(__name__)

jobConfig =   ConfigContainer.get_config(FullConfig).jobConn
config = (mysqlconfig().builder()
          .with_host(jobConfig.host)
          .with_port(jobConfig.port)
          .with_credentials(jobConfig.username, jobConfig.password    )
          .with_database(jobConfig.database)
          .with_table_name('zvt_scheduled_jobs')
          .build())
# MySQL 数据库配置
# mysql_host = "localhost"  # 修改为你的MySQL主机
# mysql_port = 3306         # 修改为你的MySQL端口
# mysql_db = "zvt_jobs"     # 修改为你的数据库名
# mysql_user = "root"   # 修改为你的MySQL用户名
# mysql_password = "root"  # 修改为你的MySQL密码
# mysql_table = "zvt_scheduled_jobs"  # 自定义表名
#jobstores = {"default": SQLAlchemyJobStore(url=f"sqlite:///{jobs_db_path}")}
#url =  url=f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}",
# 使用MySQL作为作业存储
jobstores = {
    "default": SQLAlchemyJobStore(
        url= config.get_connection_url(),
        engine_options={
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
            "connect_args": {
                "charset": "utf8mb4"
            }
        }
    )
}

executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 1}

zvt_scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)


def sched_tasks():
    print()
    # import platform
    #
    # if platform.system() == "Windows":
    #     try:
    #         from core.broker.qmt.qmt_quote import record_tick
    #
    #         zvt_scheduler.add_job(func=record_tick, trigger="cron", hour=9, minute=19, day_of_week="mon-fri")
    #     except Exception as e:
    #         logger.error("QMT not work", e)
    # else:
    #     logger.warning("QMT need run in Windows!")
    #
    # zvt_scheduler.start()


if __name__ == "__main__":
    sched_tasks()