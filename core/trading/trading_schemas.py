# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float, DateTime, Integer
from sqlalchemy import JSON
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

TradingBase = declarative_base()


class TagQuoteStats(Mixin, TradingBase):
    __tablename__ = "tag_quote_stats"
    stock_pool_name = Column(String)
    main_tag = Column(String)
    limit_up_count = Column(Integer)
    limit_down_count = Column(Integer)
    up_count = Column(Integer)
    down_count = Column(Integer)
    change_pct = Column(Float)
    turnover = Column(Float)


class TradingPlan(TradingBase, Mixin):
    __tablename__ = "trading_plan"
    stock_id = Column(String)
    stock_code = Column(String)
    stock_name = Column(String)
    trading_date = Column(DateTime)
    # 预期开盘涨跌幅
    expected_open_pct = Column(Float, nullable=False)
    buy_price = Column(Float)
    sell_price = Column(Float)
    # 操作理由
    trading_reason = Column(String)
    # 交易信号
    trading_signal_type = Column(String)
    # 执行状态
    status = Column(String)
    # 复盘
    review = Column(String)


class QueryStockQuoteSetting(TradingBase, Mixin):
    __tablename__ = "query_stock_quote_setting"
    stock_pool_name = Column(String)
    main_tags = Column(JSON)


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=TradingBase)


# the __all__ is generated
__all__ = ["TradingPlan", "QueryStockQuoteSetting"]
