# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Float, Boolean, Integer, BOOLEAN, TIMESTAMP
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract.register import register_schema
from core.contract.schema import TradableMeetActor
from core.domain.constants import stock_db_name

StockActorBase = declarative_base()


class StockTopTenFreeHolder(StockActorBase, TradableMeetActor):
    __tablename__ = "stock_top_ten_free_holder"

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 持股数
    holding_numbers = Column(Float)
    #: 持股比例
    holding_ratio = Column(Float)
    #: 持股市值
    holding_values = Column(Float)


class StockTopTenHolder(StockActorBase, TradableMeetActor):
    __tablename__ = "stock_top_ten_holder"

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 持股数
    holding_numbers = Column(Float)
    #: 持股比例
    holding_ratio = Column(Float)
    #: 持股市值
    holding_values = Column(Float)


class StockInstitutionalInvestorHolder(StockActorBase, TradableMeetActor):
    __tablename__ = "stock_institutional_investor_holder"

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 持股数
    holding_numbers = Column(Float)
    #: 持股比例
    holding_ratio = Column(Float)
    #: 持股市值
    holding_values = Column(Float)


class StockActorSummary(StockActorBase, TradableMeetActor):
    __tablename__ = "stock_actor_summary"
    #: tradable code
    code = Column(String(length=64))
    #: tradable name
    name = Column(String(length=128))

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 变动比例
    change_ratio = Column(Float)
    #: 是否完成
    is_complete = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 持股市值
    actor_type = Column(String)
    actor_count = Column(Integer)

    #: 持股数
    holding_numbers = Column(Float)
    #: 持股比例
    holding_ratio = Column(Float)
    #: 持股市值
    holding_values = Column(Float)


register_schema(providers=["em"], db_name=stock_db_name, schema_base=StockActorBase, entity_type="stock")


# the __all__ is generated
__all__ = ["StockTopTenFreeHolder", "StockTopTenHolder", "StockInstitutionalInvestorHolder", "StockActorSummary"]
