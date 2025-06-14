# -*- coding: utf-8 -*-
from sqlalchemy import Column, Boolean
from sqlalchemy.orm import declarative_base

from core.contract import TradableEntity
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

StockhkMetaBase = declarative_base()


#: 港股
@register_entity(entity_type="stockhk")
class Stockhk(StockhkMetaBase, TradableEntity):
    __tablename__ = "stockhk"
    #: 是否属于港股通
    south = Column(Boolean)

    @classmethod
    def get_trading_t(cls):
        """
        0 means t+0
        1 means t+1

        :return:
        """
        return 0

    @classmethod
    def get_trading_intervals(cls, include_bidding_time=False):
        """
        overwrite it to get the trading intervals of the entity

        :return: list of time intervals, in format [(start,end)]
        """
        if include_bidding_time:
            return [("09:15", "12:00"), ("13:00", "16:00")]
        else:
            return [("09:30", "12:00"), ("13:00", "16:00")]


register_schema(providers=["em"], db_name=stock_db_name, schema_base=StockhkMetaBase)


# the __all__ is generated
__all__ = ["Stockhk"]
