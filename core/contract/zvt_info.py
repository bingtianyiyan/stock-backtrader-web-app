# -*- coding: utf-8 -*-
from sqlalchemy import Column, Text
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract.register import register_schema
from core.contract.schema import Mixin
from core.domain.constants import stock_db_name

ZvtInfoBase = declarative_base()


class StateMixin(Mixin):
    #: the unique name of the service, e.g. recorder,factor,tag
    state_name = Column(String(length=128))

    #: json string
    state = Column(Text())


class RecorderState(ZvtInfoBase, StateMixin):
    """
    Schema for storing recorder state
    """

    __tablename__ = "recorder_state"


class TaggerState(ZvtInfoBase, StateMixin):
    """
    Schema for storing tagger state
    """

    __tablename__ = "tagger_state"


class FactorState(ZvtInfoBase, StateMixin):
    """
    Schema for storing factor state
    """

    __tablename__ = "factor_state"


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=ZvtInfoBase)


# the __all__ is generated
__all__ = ["StateMixin", "RecorderState", "TaggerState", "FactorState"]
