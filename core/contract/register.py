# -*- coding: utf-8 -*-
import logging
from typing import List

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.ddl import CreateTable
from sqlalchemy.sql.expression import text

from core.config.configmanager import ConfigContainer
from core.config.fullconfig import FullConfig
from core.contract import zvt_context
from core.contract.api import get_db_engine, get_db_session_factory
from core.contract.schema import TradableEntity, Mixin
from core.db.db_type import sqlite, mysql, postgresql
from core.utils.utils import add_to_map_list


logger = logging.getLogger(__name__)


def register_entity(entity_type: str = None):
    """
    function for register entity type

    :param entity_type:
    :type entity_type:
    :return:
    :rtype:
    """

    def register(cls):
        # register the entity
        if issubclass(cls, TradableEntity):
            entity_type_ = entity_type
            if not entity_type:
                entity_type_ = cls.__name__.lower()

            if entity_type_ not in zvt_context.tradable_entity_types:
                zvt_context.tradable_entity_types.append(entity_type_)
                zvt_context.tradable_entity_schemas.append(cls)
            zvt_context.tradable_schema_map[entity_type_] = cls
        return cls

    return register


def register_schema(
    providers: List[str],
    db_name: str,
    schema_base: DeclarativeMeta,
    entity_type: str = None,
):
    """
    function for register schema,please declare them before register

    :param providers: the supported providers for the schema
    :type providers:
    :param db_name: database name for the schema
    :type db_name:
    :param schema_base:
    :type schema_base:
    :param entity_type: the schema related entity_type
    :type entity_type:
    :return:
    :rtype:
    """
    schemas = []
    for item in schema_base.registry.mappers:
        cls = item.class_
        if type(cls) == DeclarativeMeta:
            # register provider to the schema
            for provider in providers:
                if issubclass(cls, Mixin):
                    cls.register_provider(provider)

            if zvt_context.dbname_map_schemas.get(db_name):
                schemas = zvt_context.dbname_map_schemas[db_name]
            zvt_context.schemas.append(cls)
            if entity_type:
                add_to_map_list(the_map=zvt_context.entity_map_schemas, key=entity_type, value=cls)
            schemas.append(cls)

    zvt_context.dbname_map_schemas[db_name] = schemas

    for provider in providers:
        if provider not in zvt_context.providers:
            zvt_context.providers.append(provider)

        if not zvt_context.provider_map_dbnames.get(provider):
            zvt_context.provider_map_dbnames[provider] = []
        zvt_context.provider_map_dbnames[provider].append(db_name)
        #fix 如果多个文件实体db_name一样需要追加
        #zvt_context.dbname_map_base[db_name] = schema_base
        temp_schema_base = []
        if zvt_context.dbname_map_base.get(db_name):
            temp_schema_base = zvt_context.dbname_map_schemas[db_name]
            if not schema_base in temp_schema_base:
                temp_schema_base.append(schema_base)
        else:
            temp_schema_base.append(schema_base)
        zvt_context.dbname_map_base[db_name] = temp_schema_base

        # create the db & table
        engine = get_db_engine(provider, db_name=db_name)
        schema_base.metadata.create_all(bind=engine)
        session_fac = get_db_session_factory(provider, db_name=db_name)
        session_fac.configure(bind=engine)
     #筛选出db类型
    configs = ConfigContainer.get_config(FullConfig)
    if not configs.db_configs:
        raise ValueError("db_configs should provider")
    config = next(filter(lambda x: x.database == db_name, configs.db_configs), None)
    init_table = configs.sqlinfo.initTable
    if not init_table:
        return
    for provider in providers:
        engine = get_db_engine(provider, db_name=db_name)

        # create index for 'timestamp','entity_id','code','report_period','updated_timestamp
        for table_name, table in iter(schema_base.metadata.tables.items()):
            # auto add new columns
            db_meta = MetaData()
            db_meta.reflect(bind=engine)
            db_table = db_meta.tables[table_name]
            existing_columns = [c.name for c in db_table.columns]
            added_columns = [c for c in table.columns if c.name not in existing_columns]
            index_list = []
            with engine.connect() as con:
                # FIXME: close WAL mode for saving space, most of time no need to write in multiple process
                # Database configuration based on database type
                if config.db_type == sqlite:
                    # SQLite specific configurations
                    if db_name in ("zvt_info", "stock_news", "stock_tags"):
                        # For SQLite WAL mode (better for concurrent access)
                        con.execute(text("PRAGMA journal_mode=WAL;"))
                    else:
                        # For SQLite DELETE mode (saves space)
                        con.execute(text("PRAGMA journal_mode=DELETE;"))

                    # Get index information for SQLite
                    rs = con.execute(text(f"PRAGMA index_list('{table_name}')"))
                    for row in rs:
                        index_list.append(row[1])  # SQLite returns index name in position 1

                elif config.db_type == mysql:
                    # MySQL specific configurations
                    if db_name in ("zvt_info", "stock_news", "stock_tags"):
                        # For tables that need better write performance
                        con.execute(text("SET GLOBAL innodb_flush_log_at_trx_commit = 2;"))  # Less durable but faster
                        con.execute(text("SET GLOBAL sync_binlog = 0;"))  # Disable binary log syncing for performance
                    else:
                        # For tables where durability is more important than performance
                        con.execute(text("SET GLOBAL innodb_flush_log_at_trx_commit = 1;"))  # Fully ACID compliant
                        con.execute(text("SET GLOBAL sync_binlog = 1;"))  # Safe binary log syncing

                    # Get index information for MySQL
                    rs = con.execute(text(f"SHOW INDEX FROM {table_name}"))
                    for row in rs:
                        index_list.append(row[2])  # MySQL returns index name in position 2

                elif config.db_type == postgresql:
                    # PostgreSQL specific configurations
                    # PostgreSQL doesn't need WAL mode configuration as it always uses WAL

                    # Get index information for PostgreSQL
                    rs = con.execute(text(
                        f"SELECT indexname FROM pg_indexes WHERE tablename = '{table_name}'"
                    ))
                    for row in rs:
                        index_list.append(row[0])  # PostgreSQL returns just the index name
                else:
                    raise ValueError("Unsupported database type")

                try:
                    # Using migration tool like Alembic is too complex
                    # So we just support add new column, for others just change the db manually
                    if added_columns:
                        ddl_c = engine.dialect.ddl_compiler(engine.dialect, CreateTable(table))
                        for added_column in added_columns:
                            stmt = text(
                                f"ALTER TABLE {table_name} ADD COLUMN {ddl_c.get_column_specification(added_column)}"
                            )
                            logger.info(f"{engine.url} migrations:\n {stmt}")
                            con.execute(stmt)

                    logger.debug("engine:{},table:{},index:{}".format(engine, table_name, index_list))

                    for col in [
                        "timestamp",
                        "entity_id",
                        "code",
                        "report_period",
                        "created_timestamp",
                        "updated_timestamp",
                    ]:
                        if col in table.c:
                            column = eval("table.c.{}".format(col))
                            index_name = "{}_{}_index".format(table_name, col)
                            if index_name not in index_list:
                                index = sqlalchemy.schema.Index(index_name, column)
                                try:
                                    index.create(engine)
                                    index_list.append(index_name)
                                except Exception as e:
                                    logger.error(e)

                    for cols in [("timestamp", "entity_id"), ("timestamp", "code")]:
                        if (cols[0] in table.c) and (col[1] in table.c):
                            column0 = eval("table.c.{}".format(col[0]))
                            column1 = eval("table.c.{}".format(col[1]))
                            index_name = "{}_{}_{}_index".format(table_name, col[0], col[1])
                            if index_name not in index_list:
                                index = sqlalchemy.schema.Index(index_name, column0, column1)
                                try:
                                    index.create(engine)
                                    index_list.append(index_name)
                                except Exception as e:
                                    logger.error(e)
                except Exception as e:
                    logger.error(e)
        break        #只处理一次


# the __all__ is generated
__all__ = ["register_entity", "register_schema"]
