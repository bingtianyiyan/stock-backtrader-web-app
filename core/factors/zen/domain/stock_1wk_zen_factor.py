# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base

from core.contract.register import register_schema
from core.domain.constants import stock_db_name
from core.factors.zen.domain.common import ZenFactorCommon

Stock1wkZenFactorBase = declarative_base()


class Stock1wkZenFactor(Stock1wkZenFactorBase, ZenFactorCommon):
    __tablename__ = "stock_1wk_zen_factor"


register_schema(
    providers=["zvt"], db_name=stock_db_name, schema_base=Stock1wkZenFactorBase, entity_type="stock"
)


# the __all__ is generated
__all__ = ["Stock1wkZenFactor"]
