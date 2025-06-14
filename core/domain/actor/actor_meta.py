# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_base

from core.contract.register import register_schema
from core.contract.schema import ActorEntity
from core.domain.constants import stock_db_name

ActorMetaBase = declarative_base()


#: 参与者
class ActorMeta(ActorMetaBase, ActorEntity):
    __tablename__ = "actor_meta"


register_schema(providers=["em"], db_name=stock_db_name, schema_base=ActorMetaBase)


# the __all__ is generated
__all__ = ["ActorMeta"]
