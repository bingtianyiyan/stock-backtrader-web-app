import logging
from datetime import date

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.pkg.scheduler.scheduler_manager import SchedulerManager
from internal.tasks.init_tag_system import init_tag_system_info
from internal.tasks.stock_pool_runner import record_data_and_build_stock_pools
from internal.tasks.today_shoot_runner import calculate_shoot_top
from internal.tasks.today_top_runner import calculate_top

logger = logging.getLogger(__name__)
schedulerManager = SchedulerManager(ConfigContainer.get_config(FullConfig).scheduler_config)

scheduler = schedulerManager._scheduler

@scheduler.scheduled_job(id="mytest_task",trigger='interval', seconds=10,max_instances=1,misfire_grace_time=300)
def cron_task_test():
    print('cron task is run...')
    init_tag_system_info()

#@scheduler.scheduled_job(id="system_info_task",trigger='interval', seconds=10,max_instances=1,misfire_grace_time=300)
@scheduler.scheduled_job(id="system_info_task",trigger= 'cron',minute="0",hour="5",day_of_week="1-5")
def cron_task_system_info():
    init_tag_system_info()

# @scheduler.scheduled_job(id="mytest_task2",trigger='interval', seconds=10,max_instances=1,misfire_grace_time=300)
# def today_short_runner_task():
#     print("today_short_runner_task running...")
#     init_tag_system_info()

##### @scheduler.scheduled_job(id="init_tag_system_task",trigger= 'cron',cron="0 5 * * *")

#trigger=CronTrigger.from_crontab("26 9 * * 1-5"),  # 直接解析crontab字符串
@scheduler.scheduled_job(id="today_top_task",trigger= 'cron',minute="26",hour="9",day_of_week="1-5")
def cron_task_today_top():
    #print("工作日上午9:26执行的任务")
    calculate_top()

@scheduler.scheduled_job(id="today_short_task",trigger= 'cron',minute="30",hour="9",day_of_week="1-5")
def cron_task_today_short():
    calculate_shoot_top()

@scheduler.scheduled_job(id="stock_pool_task",trigger= 'cron',hour="16",day_of_week="1-5")
def cron_task_stock_pool():
    record_data_and_build_stock_pools()
#########################

#测试用
# @scheduler.scheduled_job(id="mytest_task",trigger='interval', seconds=10,max_instances=1,misfire_grace_time=300)
# def cron_task_test():
#     print('cron task is run...')
#     init_tag_system_info()

# Scheduled tasks
# @scheduler.scheduled_job('interval', seconds=10)
# def interval_task_test():
#     print('interval task is run...')
#
# @scheduler.scheduled_job('cron', hour=3, minute=30)
# def cron_task_test():
#     print('cron task is run...')

# @scheduler.scheduled_job('date', run_date=date(2022, 11, 11))
# def date_task_test():
#     print('date task is run...')