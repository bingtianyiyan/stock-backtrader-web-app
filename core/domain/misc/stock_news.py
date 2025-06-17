# -*- coding: utf-8 -*-
from sqlalchemy import Column, JSON, Boolean, DateTime, Integer, Text, BOOLEAN
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from core.contract.data_string import String  # 使用自定义 String
from core.contract import Mixin
from core.contract.register import register_schema
from core.domain.constants import stock_db_name

NewsBase = declarative_base()


class StockNews(NewsBase, Mixin):
    __tablename__ = "stock_news"

    #: 新闻编号
    news_code = Column(String)
    #: 新闻地址
    news_url = Column(String)
    #: 新闻标题
    news_title = Column(String)
    #: 新闻内容
    news_content = Column(String)
    #: 新闻解读
    news_analysis = Column(JSON)
    #: 用户设置为忽略
    ignore_by_user = Column(Boolean().with_variant(BOOLEAN, 'postgresql').with_variant(TINYINT(1), 'mysql'), default=False)


class StockHotTopic(NewsBase, Mixin):
    __tablename__ = "stock_hot_topic"

    #: 出现时间
    created_timestamp = Column(DateTime().with_variant(TIMESTAMP(timezone=True), 'postgresql'))
    #: 热度排行
    position = Column(Integer)
    #: 相关标的
    entity_ids = Column(JSON)

    #: 新闻编号
    news_code = Column(String)
    #: 新闻标题
    news_title = Column(String)
    #: 新闻内容
    news_content = Column(Text)
    #: 新闻解读
    news_analysis = Column(JSON)


register_schema(providers=["em"], db_name=stock_db_name, schema_base=NewsBase, entity_type="stock")


# the __all__ is generated
__all__ = ["StockNews", "StockHotTopic"]
