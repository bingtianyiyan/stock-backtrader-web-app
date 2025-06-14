from sqlalchemy import String as BaseString

class String(BaseString):
    def __init__(self, length=None, **kwargs):
        # 默认长度设为255
        super().__init__(length=length or 255, **kwargs)

# the __all__ is generated
__all__ = [
    "String",
]
