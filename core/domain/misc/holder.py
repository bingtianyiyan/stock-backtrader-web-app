# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

HolderBase = declarative_base()


class HkHolder(HolderBase, Mixin):
    __tablename__ = "hk_holder"
    #: 股票代码
    code = Column(String(length=32))
    #: 股票名称
    name = Column(String(length=32))

    #: 市场通编码	三种类型：310001-沪股通，310002-深股通，310005-港股通
    holder_code = Column(String(length=32))
    #: 市场通名称	三种类型：沪股通，深股通，港股通
    holder_name = Column(String(length=32))

    #: 持股数量
    share_number = Column(Float)
    #: 持股比例
    share_ratio = Column(Float)


class TopTenTradableHolder(HolderBase, Mixin):
    __tablename__ = "top_ten_tradable_holder"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 股东代码
    holder_code = Column(String(length=32))
    #: 股东名称
    holder_name = Column(String(length=32))
    #: 持股数
    shareholding_numbers = Column(Float)
    #: 持股比例
    shareholding_ratio = Column(Float)
    #: 变动
    change = Column(Float)
    #: 变动比例
    change_ratio = Column(Float)


class TopTenHolder(HolderBase, Mixin):
    __tablename__ = "top_ten_holder"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 股东代码
    holder_code = Column(String(length=32))
    #: 股东名称
    holder_name = Column(String(length=32))
    #: 持股数
    shareholding_numbers = Column(Float)
    #: 持股比例
    shareholding_ratio = Column(Float)
    #: 变动
    change = Column(Float)
    #: 变动比例
    change_ratio = Column(Float)


class InstitutionalInvestorHolder(HolderBase, Mixin):
    __tablename__ = "institutional_investor_holder"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    report_period = Column(String(length=32))
    report_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 机构类型
    institutional_investor_type = Column(String(length=64))
    #: 股东代码
    holder_code = Column(String(length=32))
    #: 股东名称
    holder_name = Column(String(length=32))
    #: 持股数
    shareholding_numbers = Column(Float)
    #: 持股比例
    shareholding_ratio = Column(Float)


register_schema(providers=["eastmoney", "joinquant"], db_name=stock_db_name, schema_base=HolderBase, entity_type="stock")


# the __all__ is generated
__all__ = ["HkHolder", "TopTenTradableHolder", "TopTenHolder", "InstitutionalInvestorHolder"]
