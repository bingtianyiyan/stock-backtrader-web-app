#
# import logging
#
# from core.config.configmanager import ConfigContainer
# from core.config.fullconfig import FullConfig
# from core.pkg.scheduler.scheduler_manager import SchedulerManager
# from internal.tasks.stock_pool_runner import record_data_and_build_stock_pools
# from internal.tasks.today_shoot_runner import calculate_shoot_top
# from internal.tasks.today_top_runner import calculate_top
#
# logger = logging.getLogger(__name__)
#
#
# def midnight_task():
#     logger.info("Midnight task")
#     print("Midnight task")
#
# scheduler_manager = SchedulerManager(ConfigContainer.get_config(FullConfig).scheduler_config)
#
# def register_all_tasks():
#         # 添加Cron任务
#     # scheduler_manager.add_cron_task(
#     #         func= midnight_task,
#     #         cron_expr="*/5 * * * * *",  # 5秒
#     #         job_id="midnight_task2"
#     #     )
#     # logger.info("midnight_task")
#     scheduler_manager.add_cron_task(
#             func=calculate_top,
#             cron_expr="26 9 * * 1-5",
#             job_id="today_top_task"
#         )
#     logger.info("register calculate_top")
#     scheduler_manager.add_cron_task(
#             func=calculate_shoot_top,
#             cron_expr="30 9 * * 1-5",
#             job_id="today_short_task"
#         )
#     scheduler_manager.add_cron_task(
#             func=record_data_and_build_stock_pools,
#             cron_expr="0 16 * * 1-5",
#             job_id="stock_pool_task"
#         )
#     logger.info("register finish")
#     scheduler_manager.start()
#
#
# if __name__ == "__main__":
#     register_all_tasks()
#     # 保持运行
#     import time
#
#     while True:
#         time.sleep(1)
#
# __all__ = ["register_all_tasks"]