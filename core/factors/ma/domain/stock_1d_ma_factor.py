# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

Stock1dMaFactorBase = declarative_base()

@register_entity(entity_type="stock_1d_ma_factor")
class Stock1dMaFactor(Stock1dMaFactorBase, Mixin):
    __tablename__ = "stock_1d_ma_factor"

    level = Column(String(length=32))
    code = Column(String(length=32))
    name = Column(String(length=32))

    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)

    ma5 = Column(Float)
    ma10 = Column(Float)

    ma34 = Column(Float)
    ma55 = Column(Float)
    ma89 = Column(Float)
    ma144 = Column(Float)

    ma120 = Column(Float)
    ma250 = Column(Float)


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=Stock1dMaFactorBase)


# the __all__ is generated
__all__ = ["Stock1dMaFactor"]
