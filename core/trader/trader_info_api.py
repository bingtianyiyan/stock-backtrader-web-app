# -*- coding: utf-8 -*-
from typing import List, Union

import pandas as pd

from core.contract import IntervalLevel
from core.contract.api import get_data, get_db_session
from core.contract.drawer import Drawer
from core.contract.normal_data import NormalData
from core.contract.reader import DataReader
from core.trader.trader_schemas import AccountStats, Order, TraderInfo, Position


def clear_trader(trader_name, session=None):
    if not session:
        session = get_db_session("zvt", data_schema=TraderInfo)
    session.query(TraderInfo).filter(TraderInfo.trader_name == trader_name).delete()
    session.query(AccountStats).filter(AccountStats.trader_name == trader_name).delete()
    session.query(Position).filter(Position.trader_name == trader_name).delete()
    session.query(Order).filter(Order.trader_name == trader_name).delete()
    session.commit()


def get_trader_info(
    trader_name=None,
    return_type="df",
    start_timestamp=None,
    end_timestamp=None,
    filters=None,
    session=None,
    order=None,
    limit=None,
) -> List[TraderInfo]:
    if trader_name:
        if filters:
            filters = filters + [TraderInfo.trader_name == trader_name]
        else:
            filters = [TraderInfo.trader_name == trader_name]

    return get_data(
        data_schema=TraderInfo,
        entity_id=None,
        codes=None,
        level=None,
        provider="zvt",
        columns=None,
        return_type=return_type,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        filters=filters,
        session=session,
        order=order,
        limit=limit,
    )


def get_order_securities(trader_name):
    items = (
        get_db_session(provider="zvt", data_schema=Order)
        .query(Order.entity_id)
        .filter(Order.trader_name == trader_name)
        .group_by(Order.entity_id)
        .all()
    )

    return [item[0] for item in items]


class AccountStatsReader(DataReader):
    def __init__(
        self,
        start_timestamp: Union[str, pd.Timestamp] = None,
        end_timestamp: Union[str, pd.Timestamp] = None,
        columns: List = None,
        filters: List = None,
        order: object = None,
        level: IntervalLevel = IntervalLevel.LEVEL_1DAY,
        trader_names: List[str] = None,
    ) -> None:
        self.trader_names = trader_names

        self.filters = filters

        if self.trader_names:
            filter = [AccountStats.trader_name == name for name in self.trader_names]
            if self.filters:
                self.filters += filter
            else:
                self.filters = filter
        super().__init__(
            AccountStats,
            None,
            None,
            None,
            None,
            None,
            None,
            start_timestamp,
            end_timestamp,
            columns,
            self.filters,
            order,
            None,
            level,
            category_field="trader_name",
            time_field="timestamp",
            keep_window=None,
        )

    def draw_line(self, show=True):
        drawer = Drawer(
            main_data=NormalData(
                self.data_df.copy()[["trader_name", "timestamp", "all_value"]], category_field="trader_name"
            )
        )
        return drawer.draw_line(show=show)


class OrderReader(DataReader):
    def __init__(
        self,
        start_timestamp: Union[str, pd.Timestamp] = None,
        end_timestamp: Union[str, pd.Timestamp] = None,
        columns: List = None,
        filters: List = None,
        order: object = None,
        level: IntervalLevel = None,
        trader_names: List[str] = None,
    ) -> None:
        self.trader_names = trader_names

        self.filters = filters

        if self.trader_names:
            filter = [Order.trader_name == name for name in self.trader_names]
            if self.filters:
                self.filters += filter
            else:
                self.filters = filter

        super().__init__(
            Order,
            None,
            None,
            None,
            None,
            None,
            None,
            start_timestamp,
            end_timestamp,
            columns,
            self.filters,
            order,
            None,
            level,
            category_field="trader_name",
            time_field="timestamp",
            keep_window=None,
        )


if __name__ == "__main__":
    reader = AccountStatsReader(trader_names=["000338_ma_trader"])
    drawer = Drawer(
        main_data=NormalData(
            reader.data_df.copy()[["trader_name", "timestamp", "all_value"]], category_field="trader_name"
        )
    )
    drawer.draw_line()
# the __all__ is generated
__all__ = ["clear_trader", "get_trader_info", "get_order_securities", "AccountStatsReader", "OrderReader"]
