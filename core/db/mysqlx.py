from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class mysqlconfig:
    host: str = '127.0.0.1'
    port: int = 3306
    user: str = 'root'
    password: str = 'root'
    database: str = 'zvt_default'
    charset: str = 'utf8mb4'
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    table_name: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None

    @classmethod
    def builder(cls):
        return mysqlconfig.Builder()

    def get_connection_url(self):
        url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        if self.extra_params:
            params = "&".join(f"{k}={v}" for k, v in self.extra_params.items())
            url += f"?{params}"
        return url

    class Builder:
        def __init__(self):
            self._config = {
                "host": '127.0.0.1',
                "port": 3306,
                "user": 'root',
                "password": 'root',
                "database": 'zvt_default',
                "charset": 'utf8mb4',
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,
            }

        def with_host(self, host: str):
            self._config['host'] = host
            return self

        def with_port(self, port: int):
            self._config['port'] = port
            return self

        def with_credentials(self, user: str, password: str):
            self._config['user'] = user
            self._config['password'] = password
            return self

        def with_database(self, database: str):
            self._config['database'] = database
            return self

        def with_table_name(self, table_name: str):
            self._config['table_name'] = table_name
            return self

        def with_pool_settings(self, pool_size: int, max_overflow: int, pool_recycle: int):
            self._config['pool_size'] = pool_size
            self._config['max_overflow'] = max_overflow
            self._config['pool_recycle'] = pool_recycle
            return self

        def with_extra_params(self, extra_params: Dict[str, Any]):
            self._config['extra_params'] = extra_params
            return self

        def build(self):
            return mysqlconfig(**self._config)

# # 自定义配置
# custom_config = {
#     'host': '192.168.1.100',
#     'port': 3307,
#     'user': 'zvt_admin',
#     'password': 'secure_password',
#     'database': 'zvt_prod',
#     'table_name': 'zvt_custom_jobs',
#     'pool_size': 15,
#     'extra_params': {'connect_timeout': 30}
# }
#
# mysql_config = mysqlconfig.from_dict(custom_config)

# config = (mysqlconfig()
#           .with_host('db.example.com')
#           .with_port(3307)
#           .with_credentials('admin', 's3cr3t')
#           .with_database('zvt_production')
#           .with_table_name('custom_scheduler_jobs')
#           .build())