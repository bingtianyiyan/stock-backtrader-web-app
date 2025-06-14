# -*- coding: utf-8 -*-
from sqlalchemy.orm import declarative_base

from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

TradeDayBase = declarative_base()


class StockTradeDay(TradeDayBase, Mixin):
    __tablename__ = "stock_trade_day"


register_schema(providers=["joinquant"], db_name=stock_db_name, schema_base=TradeDayBase)


# the __all__ is generated
__all__ = ["StockTradeDay"]
