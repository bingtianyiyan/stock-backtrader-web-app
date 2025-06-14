# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Portfolio, PortfolioStock
from core.contract.register import register_schema, register_entity
from core.domain.constants import stock_db_name

BlockMetaBase = declarative_base()


#: 板块
@register_entity(entity_type="block")
class Block(BlockMetaBase, Portfolio):
    __tablename__ = "block"

    #: 板块类型，行业(industry),概念(concept)
    category = Column(String(length=64))


class BlockStock(BlockMetaBase, PortfolioStock):
    __tablename__ = "block_stock"


register_schema(providers=["em", "eastmoney", "sina"], db_name=stock_db_name, schema_base=BlockMetaBase)


# the __all__ is generated
__all__ = ["Block", "BlockStock"]
