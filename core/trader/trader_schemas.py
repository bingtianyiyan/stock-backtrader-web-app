# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Boolean, Float, Integer, ForeignKey, BOOLEAN, TIMESTAMP
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name
from core.utils.decorator import to_string

TraderBase = declarative_base()


class TraderInfo(TraderBase, Mixin):
    """
    trader info
    """

    __tablename__ = "trader_info"
    #: 机器人名字
    trader_name = Column(String(length=128))

    entity_type = Column(String(length=128))
    start_timestamp = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))
    end_timestamp = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))
    provider = Column(String(length=32))
    level = Column(String(length=32))
    real_time = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    kdata_use_begin_time = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    kdata_adjust_type = Column(String(length=32))


@to_string
class AccountStats(TraderBase, Mixin):
    """
    account stats of every day
    """

    __tablename__ = "account_stats"
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 明确指定存储引擎
    input_money = Column(Float)

    #: 机器人名字
    trader_name = Column(String(length=128))
    #: 可用现金
    cash = Column(Float)
    #: 具体仓位
    positions = relationship("Position", back_populates="account_stats")
    #: 市值
    value = Column(Float)
    #: 市值+cash
    all_value = Column(Float)

    #: 盈亏
    profit = Column(Float)
    #: 盈亏比例
    profit_rate = Column(Float)

    #: 收盘计算
    closing = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))


#: the position for specific entity of every day
class Position(TraderBase, Mixin):
    __tablename__ = "position"
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 明确指定存储引擎
    #: 机器人名字
    trader_name = Column(String(length=128))
    #: 账户id
    account_stats_id = Column(String, ForeignKey("account_stats.id", ondelete="CASCADE"))
    account_stats = relationship("AccountStats", back_populates="positions")

    #: 做多数量
    long_amount = Column(Float)
    #: 可平多数量
    available_long = Column(Float)
    #: 平均做多价格
    average_long_price = Column(Float)

    #: 做空数量
    short_amount = Column(Float)
    #: 可平空数量
    available_short = Column(Float)
    #: 平均做空价格
    average_short_price = Column(Float)

    #: 盈亏
    profit = Column(Float)
    #: 盈亏比例
    profit_rate = Column(Float)
    #: 市值 或者 占用的保证金(方便起见，总是100%)
    value = Column(Float)
    #: 交易类型(0代表T+0,1代表T+1)
    trading_t = Column(Integer)


#: 委托单
class Order(TraderBase, Mixin):
    __tablename__ = "orders"
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 明确指定存储引擎
    #: 机器人名字
    trader_name = Column(String(length=128))
    #: 订单价格
    order_price = Column(Float)
    #: 订单数量
    order_amount = Column(Float)
    #: 订单类型
    order_type = Column(String(length=64))
    #: 订单状态
    status = Column(String(length=64))

    #: 产生订单的selector/factor level
    level = Column(String(length=32))


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=TraderBase)

# the __all__ is generated
__all__ = ["TraderInfo", "AccountStats", "Position", "Order"]
