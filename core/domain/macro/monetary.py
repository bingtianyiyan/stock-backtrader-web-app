# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

MonetaryBase = declarative_base()


class TreasuryYield(MonetaryBase, Mixin):
    __tablename__ = "treasury_yield"

    code = Column(String(length=32))

    # 2年期
    yield_2 = Column(Float)
    # 5年期
    yield_5 = Column(Float)
    # 10年期
    yield_10 = Column(Float)
    # 30年期
    yield_30 = Column(Float)


register_schema(providers=["em"], db_name=stock_db_name, schema_base=MonetaryBase)


# the __all__ is generated
__all__ = ["TreasuryYield"]
