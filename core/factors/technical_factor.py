from typing import List, Union, Type, Optional

import pandas as pd

from core.api.kdata import default_adjust_type, get_kdata_schema
from core.contract import IntervalLevel, TradableEntity, AdjustType
from core.contract.factor import Factor, Transformer, Accumulator, FactorMeta
from core.domain import Stock


class TechnicalFactor(Factor, metaclass=FactorMeta):
    def __init__(
        self,
        entity_schema: Type[TradableEntity] = Stock,
        provider: str = None,
        entity_provider: str = None,
        entity_ids: List[str] = None,
        exchanges: List[str] = None,
        codes: List[str] = None,
        start_timestamp: Union[str, pd.Timestamp] = None,
        end_timestamp: Union[str, pd.Timestamp] = None,
        columns: List = None,
        filters: List = None,
        order: object = None,
        limit: int = None,
        level: Union[str, IntervalLevel] = IntervalLevel.LEVEL_1DAY,
        category_field: str = "entity_id",
        time_field: str = "timestamp",
        keep_window: int = None,
        keep_all_timestamp: bool = False,
        fill_method: str = "ffill",
        effective_number: int = None,
        transformer: Transformer = None,
        accumulator: Accumulator = None,
        need_persist: bool = False,
        only_compute_factor: bool = False,
        factor_name: str = None,
        clear_state: bool = False,
        only_load_factor: bool = False,
        adjust_type: Union[AdjustType, str] = None,
    ) -> None:
        if columns is None:
            columns = [
                "id",
                "entity_id",
                "timestamp",
                "level",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "turnover",
                "turnover_rate",
            ]

        # 股票默认使用后复权
        if not adjust_type:
            adjust_type = default_adjust_type(entity_type=entity_schema.__name__)

        self.adjust_type = adjust_type
        self.data_schema = get_kdata_schema(entity_schema.__name__, level=level, adjust_type=adjust_type)

        if not factor_name:
            if type(level) == str:
                factor_name = f"{type(self).__name__.lower()}_{level}"
            else:
                factor_name = f"{type(self).__name__.lower()}_{level.value}"

        super().__init__(
            self.data_schema,
            entity_schema,
            provider,
            entity_provider,
            entity_ids,
            exchanges,
            codes,
            start_timestamp,
            end_timestamp,
            columns,
            filters,
            order,
            limit,
            level,
            category_field,
            time_field,
            keep_window,
            keep_all_timestamp,
            fill_method,
            effective_number,
            transformer,
            accumulator,
            need_persist,
            only_compute_factor,
            factor_name,
            clear_state,
            only_load_factor,
        )

    def drawer_sub_df_list(self) -> Optional[List[pd.DataFrame]]:
        if self.factor_df is None:
            print("Warning: factor_df is None, returning empty list")
            return []  # 返回空列表而不是 None，避免后续处理出错
        return [self.factor_df[["volume"]]]


# the __all__ is generated
__all__ = ["TechnicalFactor"]
