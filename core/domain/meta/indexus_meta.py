# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Float
from sqlalchemy.orm import declarative_base

from core.contract import Portfolio
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

IndexusMetaBase = declarative_base()


#: 美股指数
@register_entity(entity_type="indexus")
class Indexus(IndexusMetaBase, Portfolio):
    __tablename__ = "indexus"

    #: 发布商
    publisher = Column(String(length=64))
    #: 类别
    #: see IndexCategory
    category = Column(String(length=64))
    #: 基准点数
    base_point = Column(Float)


register_schema(providers=["em"], db_name=stock_db_name, schema_base=IndexusMetaBase)


# the __all__ is generated
__all__ = ["Indexus"]
