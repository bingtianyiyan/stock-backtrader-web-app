class configmanager:
    _config = {}
    _env = {}

    @classmethod
    def update(cls, new_config : dict):
        cls._config.update(new_config)

    @classmethod
    def get(cls) -> dict:
        return cls._config.copy()

    @classmethod
    def update_env(cls, new_env : dict):
        cls._env.update(new_env)

    @classmethod
    def get_env(cls)-> dict:
        return cls._env.copy()