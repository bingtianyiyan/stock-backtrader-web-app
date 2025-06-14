# -*- coding: utf-8 -*-
from sqlalchemy.orm import declarative_base

from core.contract.register import register_schema, register_entity
from core.contract.schema import TradableEntity
from core.domain.constants import stock_db_name

FutureMetaBase = declarative_base()


@register_entity(entity_type="future")
class Future(FutureMetaBase, TradableEntity):
    __tablename__ = "future"


register_schema(providers=["em"], db_name=stock_db_name, schema_base=FutureMetaBase)


# the __all__ is generated
__all__ = ["Future"]
