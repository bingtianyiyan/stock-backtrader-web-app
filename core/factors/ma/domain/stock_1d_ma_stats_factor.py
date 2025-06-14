# -*- coding: utf-8 -*-
from sqlalchemy.orm import declarative_base

from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name
from core.factors.ma.domain.common import MaStatsFactorCommon

Stock1dMaStatsFactorBase = declarative_base()

@register_entity(entity_type="stock_1d_ma_stats_factor")
class Stock1dMaStatsFactor(Stock1dMaStatsFactorBase, MaStatsFactorCommon):
    __tablename__ = "stock_1d_ma_stats_factor"


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=Stock1dMaStatsFactorBase)


# the __all__ is generated
__all__ = ["Stock1dMaStatsFactor"]
