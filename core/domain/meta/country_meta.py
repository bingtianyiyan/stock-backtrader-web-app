# -*- coding: utf-8 -*-

from sqlalchemy import Column,  Float
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract.register import register_schema, register_entity
from core.contract.schema import TradableEntity
from core.domain.constants import stock_db_name

CountryMetaBase = declarative_base()


@register_entity(entity_type="country")
class Country(CountryMetaBase, TradableEntity):
    __tablename__ = "country"

    #: 区域
    #: region
    region = Column(String(length=128))
    #: 首都
    #: capital city
    capital_city = Column(String(length=128))
    #: 收入水平
    #: income level
    income_level = Column(String(length=64))
    #: 贷款类型
    #: lending type
    lending_type = Column(String(length=64))
    #: 经度
    #: longitude
    longitude = Column(Float)
    #: 纬度
    #: latitude
    latitude = Column(Float)


register_schema(providers=["wb"], db_name=stock_db_name, schema_base=CountryMetaBase)


# the __all__ is generated
__all__ = ["Country"]
