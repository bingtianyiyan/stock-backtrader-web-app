# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, BigInteger, Float
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import TradableEntity
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

StockMetaBase = declarative_base()


#: 个股
@register_entity(entity_type="stock")
class Stock(StockMetaBase, TradableEntity):
    __tablename__ = "stock"
    #: 股东上次更新时间
    holder_modified_date = Column(DateTime)
    #: 控股股东
    controlling_holder = Column(String)
    #: 实际控制人
    controlling_holder_parent = Column(String)
    #: 前十大股东占比
    top_ten_ratio = Column(Float)


#: 个股详情
class StockDetail(StockMetaBase, TradableEntity):
    __tablename__ = "stock_detail"

    #: 所属行业
    industries = Column(String)
    #: 行业指数
    industry_indices = Column(String)
    #: 所属板块
    concept_indices = Column(String)
    #: 所属区域
    area_indices = Column(String)

    #: 成立日期
    date_of_establishment = Column(DateTime)
    #: 公司简介
    profile = Column(String(length=1024))
    #: 主营业务
    main_business = Column(String(length=512))
    #: 发行量(股)
    issues = Column(BigInteger)
    #: 发行价格
    price = Column(Float)
    #: 募资净额(元)
    raising_fund = Column(Float)
    #: 发行市盈率
    issue_pe = Column(Float)
    #: 网上中签率
    net_winning_rate = Column(Float)


register_schema(
    providers=["exchange", "joinquant", "eastmoney", "em", "qmt"], db_name=stock_db_name, schema_base=StockMetaBase
)


# the __all__ is generated
__all__ = ["Stock", "StockDetail"]
