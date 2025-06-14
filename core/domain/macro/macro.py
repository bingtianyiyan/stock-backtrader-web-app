# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float, BIGINT
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

MacroBase = declarative_base()

#Economy 类 是一个 SQLAlchemy 模型，用于存储宏观经济数据
# 用于表示 宏观经济数据（如 GDP、人口、失业率等）
class Economy(MacroBase, Mixin):
    # https://datatopics.worldbank.org/world-development-indicators//themes/economy.html
    __tablename__ = "economy"

    code = Column(String(length=32))
    name = Column(String(length=32))
    population = Column(BIGINT)

    gdp = Column(Float)
    gdp_per_capita = Column(Float)
    gdp_per_employed = Column(Float)
    gdp_growth = Column(Float)
    agriculture_growth = Column(Float)
    industry_growth = Column(Float)
    manufacturing_growth = Column(Float)
    service_growth = Column(Float)
    consumption_growth = Column(Float)
    capital_growth = Column(Float)
    exports_growth = Column(Float)
    imports_growth = Column(Float)

    gni = Column(Float)
    gni_per_capita = Column(Float)

    gross_saving = Column(Float)
    cpi = Column(Float)
    unemployment_rate = Column(Float)
    fdi_of_gdp = Column(Float)


register_schema(providers=["wb"], db_name=stock_db_name, schema_base=MacroBase)


# the __all__ is generated
__all__ = ["Economy"]
