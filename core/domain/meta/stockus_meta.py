# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_base

from core.contract import TradableEntity
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

StockusMetaBase = declarative_base()


#: 美股
@register_entity(entity_type="stockus")
class Stockus(StockusMetaBase, TradableEntity):
    __tablename__ = "stockus"


register_schema(providers=["em"], db_name=stock_db_name, schema_base=StockusMetaBase)


# the __all__ is generated
__all__ = ["Stockus"]
