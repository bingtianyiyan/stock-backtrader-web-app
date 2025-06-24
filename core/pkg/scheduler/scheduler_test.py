from core.pkg.scheduler.config import SchedulerConfig, DbStoreArgs
from core.pkg.scheduler.scheduler_manager import SchedulerManager

def midnight_task():
    print("Midnight task")

if __name__ == "__main__":
#def test():
    # 配置PostgreSQL存储
    config = SchedulerConfig(
        jobstore_type='mysql',
        args= DbStoreArgs( database_url= 'mysql+pymysql://root:root@localhost/tinyjobs') ,
        max_workers=10
    )

    # 初始化管理器
    with SchedulerManager(config) as manager:
        # 添加间隔任务
        manager.add_interval_task(
            func=midnight_task,
            interval=30,  # 30秒间隔
            job_id="print_task"
        )

        # 添加Cron任务
        manager.add_cron_task(
            func=midnight_task,
            cron_expr="*/5 * * * * *",  # 5秒
            job_id="midnight_task"
        )
        manager.start()
        # 获取任务信息
        print(manager.get_task_info("print_task"))

        # 保持运行
        import time
        while True:
         time.sleep(1)