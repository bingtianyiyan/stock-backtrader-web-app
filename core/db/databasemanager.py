from typing import Optional, Union
from sqlalchemy import create_engine, Engine, text, URL
from sqlalchemy.exc import OperationalError, ProgrammingError
import json
import logging
from threading import Lock

from core.config.fullconfig import DatabaseConfig
from core.db.db_type import mysql, postgresql, sqlite

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    _engines = {}
    _lock = Lock()

    @classmethod
    def get_engine(
            cls,
            provider: str,
            db_name: str,
            config: Optional[DatabaseConfig] = None
    ) -> Engine:
        """获取或创建数据库引擎"""
        engine_key = f"{provider}_{db_name}"

        with cls._lock:
            if engine_key in cls._engines:
                return cls._engines[engine_key]

            # 获取或创建默认配置
            if config is None:
                config = cls._get_default_config(db_name)

            # 创建引擎
            engine = cls._create_engine(config)

            # 验证并创建数据库（如需要）
            cls._ensure_database_exists(config, engine)

            cls._engines[engine_key] = engine
            return engine

    @classmethod
    def _get_default_config(cls, db_name: str) -> DatabaseConfig:
        """获取默认配置（可根据实际项目调整）"""
        return DatabaseConfig(
            db_type=mysql,
            host="127.0.0.1",
            port=3306,
            username="root",
            password="root",
            database=db_name
        )

    @classmethod
    def _create_engine(cls, config: DatabaseConfig) -> Engine:
        """根据配置创建SQLAlchemy引擎"""
        if config.db_type == "sqlite":
            # provider_path = os.path.join(data_path, provider)
            # if not os.path.exists(provider_path):
            #     os.makedirs(provider_path)
            # db_path = os.path.join(provider_path, "{}_{}.db?check_same_thread=False".format(provider, db_name))
            #这边上面需要改造，暂时用不到
            return create_engine(
                f"sqlite:///{config.database}.db",
                connect_args={"check_same_thread": False},
                json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
                echo=config.echo
            )

        # 处理MySQL/PostgreSQL
        drivername = {
            mysql: "mysql+pymysql",
            postgresql: "postgresql+psycopg2"
        }[config.db_type]

        port = config.port or (3306 if config.db_type == mysql else 5432)

        # 构建连接URL
        url_params = {
            "drivername": drivername,
            "username": config.username,
            "password": config.password,
            "host": config.host,
            "port": port,
            "database": config.database
        }

        if config.db_type == mysql:
            url_params["query"] = {"charset": config.extra.charset}
        elif config.db_type == "postgresql":
            url_params["query"] = {"options": f"-csearch_path={config.pg_config.schema_}"}

        engine = create_engine(
            URL.create(**url_params),
            pool_size=config.extra.pool_size,
            max_overflow=config.extra.max_overflow,
            pool_recycle=config.extra.pool_recycle,
            pool_pre_ping=True,
            echo=config.extra.echo,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
        )
        # 添加方言特定配置
        if config.db_type == "postgresql":
            engine.dialect.identifier_preparer.initial_quote = '"'
            engine.dialect.identifier_preparer.final_quote = '"'
        elif config.db_type == mysql:
            engine.dialect.identifier_preparer.initial_quote = '`'
            engine.dialect.identifier_preparer.final_quote = '`'
        return engine

    @classmethod
    def _ensure_database_exists(cls, config: DatabaseConfig, engine: Engine) -> None:
        """确保数据库存在，如不存在则自动创建"""
        if config.db_type == sqlite:
            return  # SQLite文件会自动创建

        try:
            # 测试连接是否有效
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database {config.database} connection successful")
        except (OperationalError, ProgrammingError) as e:
            error_msg = str(e).lower()
            if "unknown database" in error_msg and config.db_type == mysql:
                cls._create_mysql_database(config)
            elif ("does not exist" in error_msg or "database \"" + config.database.lower() + "\"" in error_msg) and config.db_type == postgresql:
                cls._create_postgresql_database(config)
            else:
                raise

    @classmethod
    def _create_mysql_database(cls, config: DatabaseConfig) -> None:
        """创建MySQL数据库"""
        from sqlalchemy import create_engine

        logger.info(f"Creating MySQL database: {config.database}")

        # 连接到MySQL服务器（不指定数据库）
        admin_url = URL.create(
            drivername="mysql+pymysql",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port or 3306,
            database=mysql
        )

        admin_engine = create_engine(admin_url)

        try:
            with admin_engine.connect() as conn:
                # 创建数据库
                 conn.execute(
                             text(f"CREATE DATABASE IF NOT EXISTS {config.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                # conn.execute(text(
                #     f"CREATE DATABASE {config.database} CHARACTER SET {config.extra.charset} COLLATE {config.extra.charset}_unicode_ci"))
                # 授予权限（根据实际情况调整）
                # conn.execute(text(f"GRANT ALL PRIVILEGES ON {config.database}.* TO '{config.username}'@'%'"))
                # conn.execute(text("FLUSH PRIVILEGES"))
        finally:
            admin_engine.dispose()

    @classmethod
    def _create_postgresql_database(cls, config: DatabaseConfig) -> None:
        """创建PostgreSQL数据库"""
        from sqlalchemy import create_engine

        logger.info(f"Creating PostgreSQL database: {config.database}")

        # 连接到postgres默认数据库
        admin_url = URL.create(
            drivername="postgresql+psycopg2",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port or 5432,
            database="postgres",
        )

        admin_engine = create_engine(admin_url,isolation_level="AUTOCOMMIT")

        try:
            with admin_engine.connect() as conn:
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {config.database} ENCODING 'UTF8'"))
                # 创建schema（如果指定了非public的schema）
                if config.schema_ != "public":
                    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {config.pg_config.schema}"))
        finally:
            admin_engine.dispose()

    @classmethod
    def close_all(cls):
        """关闭所有数据库连接"""
        with cls._lock:
            for engine in cls._engines.values():
                engine.dispose()
            cls._engines.clear()



