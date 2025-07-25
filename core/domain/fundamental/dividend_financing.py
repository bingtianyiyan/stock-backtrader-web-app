# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

DividendFinancingBase = declarative_base()


class DividendFinancing(DividendFinancingBase, Mixin):
    __tablename__ = "dividend_financing"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    #: 分红总额
    dividend_money = Column(Float)

    #: 新股
    ipo_issues = Column(Float)
    ipo_raising_fund = Column(Float)

    #: 增发
    spo_issues = Column(Float)
    spo_raising_fund = Column(Float)
    #: 配股
    rights_issues = Column(Float)
    rights_raising_fund = Column(Float)


class DividendDetail(DividendFinancingBase, Mixin):
    __tablename__ = "dividend_detail"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    #: 公告日
    announce_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))
    #: 股权登记日
    record_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))
    #: 除权除息日
    dividend_date = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))

    #: 方案
    dividend = Column(String(length=128))


class SpoDetail(DividendFinancingBase, Mixin):
    __tablename__ = "spo_detail"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    spo_issues = Column(Float)
    spo_price = Column(Float)
    spo_raising_fund = Column(Float)


class RightsIssueDetail(DividendFinancingBase, Mixin):
    __tablename__ = "rights_issue_detail"

    provider = Column(String(length=32))
    code = Column(String(length=32))

    #: 配股
    rights_issues = Column(Float)
    rights_issue_price = Column(Float)
    rights_raising_fund = Column(Float)


register_schema(
    providers=["eastmoney"], db_name=stock_db_name, schema_base=DividendFinancingBase, entity_type="stock"
)


# the __all__ is generated
__all__ = ["DividendFinancing", "DividendDetail", "SpoDetail", "RightsIssueDetail"]
