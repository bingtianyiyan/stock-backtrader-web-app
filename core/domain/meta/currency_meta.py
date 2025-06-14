# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_base

from core.contract.register import register_schema, register_entity
from core.contract.schema import TradableEntity
from core.domain.constants import stock_db_name

CurrencyMetaBase = declarative_base()


@register_entity(entity_type="currency")
class Currency(CurrencyMetaBase, TradableEntity):
    __tablename__ = "currency"


register_schema(providers=["em"], db_name=stock_db_name, schema_base=CurrencyMetaBase)


# the __all__ is generated
__all__ = ["Currency"]
