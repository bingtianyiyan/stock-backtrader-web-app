from urllib.parse import urlparse, urlunparse
from typing import Optional


def async_to_sync_db_url(async_url: str) -> Optional[str]:
    """将异步数据库URL转换为同步URL"""
    if not async_url:
        return None

    parsed = urlparse(async_url)

    # 处理不同数据库方言
    scheme = parsed.scheme
    if "+" in scheme:  # 包含异步驱动标识
        base_scheme = scheme.split("+")[0]

        # 主流数据库转换规则
        conversion_rules = {
            # MySQL/MariaDB
            "mysql": {"asyncmy": "pymysql", "aiomysql": "pymysql"},
            # PostgreSQL
            "postgresql": {"asyncpg": "psycopg2", "psycopg": "psycopg2"},
            # SQLite
            "sqlite": {"aiosqlite": None},  # SQLite无需同步驱动
            # Microsoft SQL Server
            "mssql": {"asyncodbc": "pyodbc"},
            # Oracle
            "oracle": {"async_oracle": "cx_oracle"}
        }

        # 应用转换规则
        for db_type, drivers in conversion_rules.items():
            if base_scheme.startswith(db_type):
                async_driver = scheme.split("+")[1]
                sync_driver = drivers.get(async_driver)
                new_scheme = f"{base_scheme}+{sync_driver}" if sync_driver else base_scheme
                return urlunparse(parsed._replace(scheme=new_scheme))

    # 未知类型原样返回（可能已经是同步URL）
    return async_url