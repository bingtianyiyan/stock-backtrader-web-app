# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float, Integer, Boolean, JSON, BOOLEAN
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name
from core.domain.quotes import StockKdataCommon

StockQuoteBase = declarative_base()


class StockTick(StockQuoteBase, Mixin):
    __tablename__ = "stock_tick"

    code = Column(String(length=32))

    #: UNIX时间戳
    time = Column(Integer)
    #: 最新价
    lastPrice = Column(Float)

    # 开盘价
    open = Column(Float)
    # 最高价
    high = Column(Float)
    # 最低价
    low = Column(Float)
    # 上日收盘价
    lastClose = Column(Float)

    amount = Column(Float)
    volume = Column(Float)
    pvolume = Column(Float)

    askPrice = Column(JSON)
    askVol = Column(JSON)
    bidPrice = Column(JSON)
    bidVol = Column(JSON)


class StockQuote(StockQuoteBase, StockKdataCommon):
    __tablename__ = "stock_quote"
    #: UNIX时间戳
    time = Column(Integer)
    #: 最新价
    price = Column(Float)
    #: 是否涨停
    is_limit_up = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 封涨停金额
    limit_up_amount = Column(Float)
    #: 是否跌停
    is_limit_down = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 封跌停金额
    limit_down_amount = Column(Float)
    #: 5挡卖单金额
    ask_amount = Column(Float)
    #: 5挡买单金额
    bid_amount = Column(Float)
    #: 流通市值
    float_cap = Column(Float)
    #: 总市值
    total_cap = Column(Float)


class StockQuoteLog(StockQuoteBase, StockKdataCommon):
    __tablename__ = "stock_quote_log"
    #: UNIX时间戳
    time = Column(Integer)
    #: 最新价
    price = Column(Float)
    #: 是否涨停
    is_limit_up = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 封涨停金额
    limit_up_amount = Column(Float)
    #: 是否跌停
    is_limit_down = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 封跌停金额
    limit_down_amount = Column(Float)
    #: 5挡卖单金额
    ask_amount = Column(Float)
    #: 5挡买单金额
    bid_amount = Column(Float)
    #: 流通市值
    float_cap = Column(Float)
    #: 总市值
    total_cap = Column(Float)


class Stock1mQuote(StockQuoteBase, Mixin):
    __tablename__ = "stock_1m_quote"
    code = Column(String(length=32))
    name = Column(String(length=32))

    #: UNIX时间戳
    time = Column(Integer)
    #: 最新价
    price = Column(Float)
    #: 均价
    avg_price = Column(Float)
    # 涨跌幅
    change_pct = Column(Float)
    # 成交量
    volume = Column(Float)
    # 成交金额
    turnover = Column(Float)
    # 换手率
    turnover_rate = Column(Float)
    #: 是否涨停
    is_limit_up = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 是否跌停
    is_limit_down = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))


register_schema(providers=["qmt"], db_name=stock_db_name, schema_base=StockQuoteBase, entity_type="stock")


# the __all__ is generated
__all__ = ["StockQuote", "StockQuoteLog", "Stock1mQuote"]
