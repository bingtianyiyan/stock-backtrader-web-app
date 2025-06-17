# -*- coding: utf-8 -*-

from sqlalchemy import Column, JSON, Boolean, Float, Integer, Text, BOOLEAN
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

StockTagsBase = declarative_base()


class IndustryInfo(StockTagsBase, Mixin):
    __tablename__ = "industry_info"

    industry_name = Column(String, unique=True)
    description = Column(String)
    # related main tag
    main_tag = Column(String)


class MainTagInfo(StockTagsBase, Mixin):
    __tablename__ = "main_tag_info"

    tag = Column(String, unique=True)
    tag_reason = Column(Text)


class SubTagInfo(StockTagsBase, Mixin):
    __tablename__ = "sub_tag_info"

    tag = Column(String, unique=True)
    tag_reason = Column(String)

    # related main tag
    main_tag = Column(String)


class HiddenTagInfo(StockTagsBase, Mixin):
    __tablename__ = "hidden_tag_info"

    tag = Column(String, unique=True)
    tag_reason = Column(String)


class StockTags(StockTagsBase, Mixin):
    """
    Schema for storing stock tags
    """

    __tablename__ = "stock_tags"

    code = Column(String(length=64))
    name = Column(String(length=128))

    main_tag = Column(String)
    main_tag_reason = Column(String)
    main_tags = Column(JSON)

    sub_tag = Column(String)
    sub_tag_reason = Column(String)
    sub_tags = Column(JSON)

    active_hidden_tags = Column(JSON)
    hidden_tags = Column(JSON)
    set_by_user = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'), default=False)


class StockSystemTags(StockTagsBase, Mixin):
    __tablename__ = "stock_system_tags"
    #: 编码
    code = Column(String(length=64))
    #: 名字
    name = Column(String(length=128))
    #: 减持
    recent_reduction = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 增持
    recent_acquisition = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 解禁
    recent_unlock = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 增发配股
    recent_additional_or_rights_issue = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 业绩利好
    recent_positive_earnings_news = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 业绩利空
    recent_negative_earnings_news = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 上榜次数
    recent_dragon_and_tiger_count = Column(Integer)
    #: 违规行为
    recent_violation_alert = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 利好
    recent_positive_news = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 利空
    recent_negative_news = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    #: 新闻总结
    recent_news_summary = Column(JSON)


class StockPoolInfo(StockTagsBase, Mixin):
    __tablename__ = "stock_pool_info"
    stock_pool_type = Column(String)
    stock_pool_name = Column(String, unique=True)


class StockPools(StockTagsBase, Mixin):
    __tablename__ = "stock_pools"
    stock_pool_name = Column(String)
    entity_ids = Column(JSON)


class TagStats(StockTagsBase, Mixin):
    __tablename__ = "tag_stats"

    stock_pool_name = Column(String)
    main_tag = Column(String)
    turnover = Column(Float)
    entity_count = Column(Integer)
    position = Column(Integer)
    is_main_line = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'))
    main_line_continuous_days = Column(Integer)
    entity_ids = Column(JSON)


register_schema(providers=["zvt"], db_name=stock_db_name, schema_base=StockTagsBase)


# the __all__ is generated
__all__ = [
    "IndustryInfo",
    "MainTagInfo",
    "SubTagInfo",
    "HiddenTagInfo",
    "StockTags",
    "StockSystemTags",
    "StockPoolInfo",
    "StockPools",
    "TagStats",
]
