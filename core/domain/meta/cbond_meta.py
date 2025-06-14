# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_base

from core.contract import TradableEntity
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

CBondBase = declarative_base()


#: 美股
@register_entity(entity_type="cbond")
class CBond(CBondBase, TradableEntity):
    __tablename__ = "cbond"


register_schema(providers=["em"], db_name=stock_db_name, schema_base=CBondBase)


# the __all__ is generated
__all__ = ["CBond"]
