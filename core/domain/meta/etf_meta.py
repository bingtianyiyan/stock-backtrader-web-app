# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Portfolio, PortfolioStockHistory
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name
from core.utils.time_utils import now_pd_timestamp

EtfMetaBase = declarative_base()


#: etf
@register_entity(entity_type="etf")
class Etf(EtfMetaBase, Portfolio):
    __tablename__ = "etf"
    category = Column(String(length=64))

    @classmethod
    def get_stocks(cls, code=None, codes=None, ids=None, timestamp=now_pd_timestamp(), provider=None):
        from core.api import get_etf_stocks

        return get_etf_stocks(code=code, codes=codes, ids=ids, timestamp=timestamp, provider=provider)


class EtfStock(EtfMetaBase, PortfolioStockHistory):
    __tablename__ = "etf_stock"


register_schema(providers=["exchange", "joinquant"], db_name=stock_db_name, schema_base=EtfMetaBase)


# the __all__ is generated
__all__ = ["Etf", "EtfStock"]
