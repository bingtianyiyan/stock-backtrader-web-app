import datetime
from attr import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AkshareParams(BaseModel):
    """AkshareParams 模型"""

    symbol: str
    period: str
    start_date: str
    end_date: str
    adjust: str


class BacktraderParams(BaseModel):
    """BacktraderParams 模型"""

    start_date: datetime.date
    end_date: datetime.date
    start_cash: float
    commission_fee: float
    stake: int


class StrategyBase(BaseModel):
    """策略基础模型"""
    name: str
    params: Dict[str, Any]

@dataclass
class Stock:
    code: str
    name: str
    market: str
    sector: Optional[str] = None
    listing_date: Optional[str] = None
    pe_ratio: Optional[float] = None