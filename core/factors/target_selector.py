import operator
from enum import Enum
from itertools import accumulate
from typing import List, Optional

import pandas as pd
from pandas import DataFrame

from core.contract import IntervalLevel
from core.contract.factor import Factor
from core.domain.meta.stock_meta import Stock
from core.utils.pd_utils import index_df, pd_is_not_null, is_filter_result_df, is_score_result_df
from core.utils.time_utils import to_pd_timestamp, now_pd_timestamp


class TradeType(Enum):
    # open_long 代表开多，并应该平掉相应标的的空单
    open_long = "open_long"
    # open_short 代表开空，并应该平掉相应标的的多单
    open_short = "open_short"
    # keep 代表保持现状，跟主动开仓有区别，有时有仓位是可以保持的，但不适合开新的仓
    keep = "keep"


class SelectMode(Enum):
    condition_and = "condition_and"
    condition_or = "condition_or"


class TargetSelector(object):
    def __init__(
        self,
        entity_ids=None,
        entity_schema=Stock,
        exchanges=None,
        codes=None,
        start_timestamp=None,
        end_timestamp=None,
        long_threshold=0.8,
        short_threshold=0.2,
        level=IntervalLevel.LEVEL_1DAY,
        provider=None,
        select_mode: SelectMode = SelectMode.condition_and,
    ) -> None:
        self.entity_ids = entity_ids
        self.entity_schema = entity_schema
        self.exchanges = exchanges
        self.codes = codes
        self.provider = provider
        self.select_mode = select_mode

        if start_timestamp:
            self.start_timestamp = to_pd_timestamp(start_timestamp)
        if end_timestamp:
            self.end_timestamp = to_pd_timestamp(end_timestamp)
        else:
            self.end_timestamp = now_pd_timestamp()

        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.level = level

        self.factors: List[Factor] = []
        self.filter_result = None
        self.score_result = None

        self.open_long_df: Optional[DataFrame] = None
        self.open_short_df: Optional[DataFrame] = None
        self.keep_df: Optional[DataFrame] = None

        self.init_factors(
            entity_ids=entity_ids,
            entity_schema=entity_schema,
            exchanges=exchanges,
            codes=codes,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            level=self.level,
        )

    def init_factors(self, entity_ids, entity_schema, exchanges, codes, start_timestamp, end_timestamp, level):
        pass

    def add_factor(self, factor: Factor):
        self.check_factor(factor)
        self.factors.append(factor)
        return self

    def check_factor(self, factor: Factor):
        assert factor.level == self.level

    def move_on(self, to_timestamp=None, kdata_use_begin_time=False, timeout=20):
        if self.factors:
            for factor in self.factors:
                factor.move_on(to_timestamp, timeout=timeout)

        self.run()

    def run(self):
        """ """
        if self.factors:
            filters = []
            scores = []
            for factor in self.factors:
                if is_filter_result_df(factor.result_df):
                    df = factor.result_df[["filter_result"]]
                    if pd_is_not_null(df):
                        df.columns = ["score"]
                        filters.append(df)
                    else:
                        raise Exception("no data for factor:{},{}".format(factor.name, factor))
                if is_score_result_df(factor.result_df):
                    df = factor.result_df[["score_result"]]
                    if pd_is_not_null(df):
                        df.columns = ["score"]
                        scores.append(df)
                    else:
                        raise Exception("no data for factor:{},{}".format(factor.name, factor))

            if filters:
                if self.select_mode == SelectMode.condition_and:
                    self.filter_result = list(accumulate(filters, func=operator.__and__))[-1]
                else:
                    self.filter_result = list(accumulate(filters, func=operator.__or__))[-1]

            if scores:
                self.score_result = list(accumulate(scores, func=operator.__add__))[-1] / len(scores)

        self.generate_targets()

    def get_targets(self, timestamp, trade_type: TradeType = TradeType.open_long) -> List[str]:
        if trade_type == TradeType.open_long:
            df = self.open_long_df
        elif trade_type == TradeType.open_short:
            df = self.open_short_df
        elif trade_type == TradeType.keep:
            df = self.keep_df
        else:
            assert False

        if pd_is_not_null(df):
            if timestamp in df.index:
                target_df = df.loc[[to_pd_timestamp(timestamp)], :]
                return target_df["entity_id"].tolist()
        return []

    def get_targets_between(
        self, start_timestamp, end_timestamp, trade_type: TradeType = TradeType.open_long
    ) -> List[str]:
        if trade_type == TradeType.open_long:
            df = self.open_long_df
        elif trade_type == TradeType.open_short:
            df = self.open_short_df
        elif trade_type == TradeType.keep:
            df = self.keep_df
        else:
            assert False

        if pd_is_not_null(df):
            index = pd.date_range(start_timestamp, end_timestamp, freq=self.level.to_pd_freq())
            return list(set(df.loc[df.index & index]["entity_id"].tolist()))
        return []

    def get_open_long_targets(self, timestamp):
        return self.get_targets(timestamp=timestamp, trade_type=TradeType.open_long)

    def get_open_short_targets(self, timestamp):
        return self.get_targets(timestamp=timestamp, trade_type=TradeType.open_short)

    # overwrite it to generate targets
    def generate_targets(self):
        keep_result = pd.DataFrame()
        long_result = pd.DataFrame()
        short_result = pd.DataFrame()

        if pd_is_not_null(self.filter_result):
            keep_result = self.filter_result[self.filter_result["score"].isna()]
            long_result = self.filter_result[self.filter_result["score"] == True]
            short_result = self.filter_result[self.filter_result["score"] == False]

        if pd_is_not_null(self.score_result):
            score_keep_result = self.score_result[
                (self.score_result["score"] > self.short_threshold) & (self.score_result["score"] < self.long_threshold)
            ]
            if pd_is_not_null(keep_result):
                keep_result = score_keep_result.loc[keep_result.index, :]
            else:
                keep_result = score_keep_result

            score_long_result = self.score_result[self.score_result["score"] >= self.long_threshold]
            if pd_is_not_null(long_result):
                long_result = score_long_result.loc[long_result.index, :]
            else:
                long_result = score_long_result

            score_short_result = self.score_result[self.score_result["score"] <= self.short_threshold]
            if pd_is_not_null(short_result):
                short_result = score_short_result.loc[short_result.index, :]
            else:
                short_result = score_short_result

        self.keep_df = self.normalize_result_df(keep_result)
        self.open_long_df = self.normalize_result_df(long_result)
        self.open_short_df = self.normalize_result_df(short_result)

    def get_result_df(self):
        return self.open_long_df

    def normalize_result_df(self, df):
        if pd_is_not_null(df):
            df = df.reset_index()
            df = index_df(df)
            df = df.sort_values(by=["score", "entity_id"])
        return df


# the __all__ is generated
__all__ = ["TradeType", "SelectMode", "TargetSelector"]
