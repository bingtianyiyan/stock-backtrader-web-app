# -*- coding: utf-8 -*-
import logging
import time
import eastmoneypy

from core.api.selector import get_shoot_today
from core.domain import Stock
from core.informer.inform_utils import add_to_eastmoney
from core.tag.common import InsertMode
from core.tag.tag_stats import build_stock_pool_and_tag_stats
from core.utils.time_utils import now_pd_timestamp, current_date

logger = logging.getLogger(__name__)


# sched = BackgroundScheduler()


def calculate_shoot_top():
    try:
        eastmoneypy.del_group("今日异动")
    except:
        pass
    while True:
        current_timestamp = now_pd_timestamp()

        if not Stock.in_trading_time():
            logger.info(f"calculate shoots finished at: {current_timestamp}")
            break

        if Stock.in_trading_time() and not Stock.in_real_trading_time():
            logger.info("Sleeping time......")
            time.sleep(60 * 1)
            continue

        target_date = current_date()
        shoot_up, shoot_down = get_shoot_today()

        shoots = shoot_up + shoot_down
        if shoots:
            build_stock_pool_and_tag_stats(
                entity_ids=shoots,
                stock_pool_name="今日异动",
                insert_mode=InsertMode.append,
                target_date=target_date,
                provider="qmt",
            )
            add_to_eastmoney(codes=[entity_id.split("_")[2] for entity_id in shoots], group="今日异动", over_write=False)

        logger.info(f"Sleep 1 minutes to compute {target_date} shoots tag stats")
        time.sleep(60 * 1)


if __name__ == "__main__":
    #init_log("today_shoot_runner.log")
     calculate_shoot_top()
    # sched.add_job(func=calculate_shoot_top, trigger="cron", hour=9, minute=30, day_of_week="mon-fri")
    # sched.start()
    # sched._thread.join()
    # scheduler_manager.add_cron_task(
    #         func=calculate_shoot_top(),
    #         cron_expr="30 9 * * 1-5",
    #         job_id="today_short_task"
    #     )
