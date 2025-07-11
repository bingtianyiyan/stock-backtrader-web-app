# -*- coding: utf-8 -*-
import pandas as pd

from core.api.kdata import get_kdata_schema
# from core.api import get_kdata_schema, get_kdata
# from core.broker.qmt import qmt_quote
from core.contract import IntervalLevel, AdjustType
from core.contract.api import df_to_db, get_db_session, get_entities
from core.contract.recorder import FixedCycleDataRecorder
from core.domain import (
    Stock,
    StockKdataCommon,
)
from core.utils.pd_utils import pd_is_not_null
from core.utils.time_utils import current_date, to_time_str, now_time_str


class BaseQmtKdataRecorder(FixedCycleDataRecorder):
    default_size = 50000
    entity_provider: str = "qmt"

    provider = "qmt"

    def __init__(
        self,
        force_update=True,
        sleeping_time=10,
        exchanges=None,
        entity_id=None,
        entity_ids=None,
        code=None,
        codes=None,
        day_data=False,
        entity_filters=None,
        ignore_failed=True,
        real_time=False,
        fix_duplicate_way="ignore",
        start_timestamp=None,
        end_timestamp=None,
        level=IntervalLevel.LEVEL_1DAY,
        kdata_use_begin_time=False,
        one_day_trading_minutes=24 * 60,
        adjust_type=AdjustType.qfq,
        return_unfinished=False,
    ) -> None:
        level = IntervalLevel(level)
        self.adjust_type = AdjustType(adjust_type)
        self.entity_type = self.entity_schema.__name__.lower()

        self.data_schema = get_kdata_schema(entity_type=self.entity_type, level=level, adjust_type=self.adjust_type)

        super().__init__(
            force_update,
            sleeping_time,
            exchanges,
            entity_id,
            entity_ids,
            code,
            codes,
            day_data,
            entity_filters,
            ignore_failed,
            real_time,
            fix_duplicate_way,
            start_timestamp,
            end_timestamp,
            level,
            kdata_use_begin_time,
            one_day_trading_minutes,
            return_unfinished,
        )

    def init_entities(self):
        """
        init the entities which we would record data for

        """
        if self.entity_provider == self.provider and self.entity_schema == self.data_schema:
            self.entity_session = self.session
        else:
            self.entity_session = get_db_session(provider=self.entity_provider, data_schema=self.entity_schema)

        if self.day_data:
            df = self.data_schema.query_data(
                start_timestamp=now_time_str(), columns=["entity_id", "timestamp"], provider=self.provider
            )
            if pd_is_not_null(df):
                entity_ids = df["entity_id"].tolist()
                self.logger.info(f"ignore entity_ids:{entity_ids}")
                if self.entity_filters:
                    self.entity_filters.append(self.entity_schema.entity_id.notin_(entity_ids))
                else:
                    self.entity_filters = [self.entity_schema.entity_id.notin_(entity_ids)]

        #: init the entity list
        self.entities = get_entities(
            session=self.entity_session,
            entity_schema=self.entity_schema,
            exchanges=self.exchanges,
            entity_ids=self.entity_ids,
            codes=self.codes,
            return_type="domain",
            provider=self.entity_provider,
            filters=self.entity_filters,
        )

    def record(self, entity, start, end, size, timestamps):
        if start and (self.level == IntervalLevel.LEVEL_1DAY):
            start = start.date()

        # 判断是否需要重新计算之前保存的前复权数据
        # if start and (self.adjust_type == AdjustType.qfq):
        #     # check_df = qmt_quote.get_kdata(
        #     #     entity_id=entity.id,
        #     #     start_timestamp=start,
        #     #     end_timestamp=start,
        #     #     adjust_type=self.adjust_type,
        #     #     level=self.level,
        #     #     download_history=False,
        #     # )
        #     # if pd_is_not_null(check_df):
        #     #     current_df = get_kdata(
        #     #         entity_id=entity.id,
        #     #         provider=self.provider,
        #     #         start_timestamp=start,
        #     #         end_timestamp=start,
        #     #         limit=1,
        #     #         level=self.level,
        #     #         adjust_type=self.adjust_type,
        #     #     )
        #     #     if pd_is_not_null(current_df):
        #     #         old = current_df.iloc[0, :]["close"]
        #     #         new = check_df["close"][0]
        #     #         # 相同时间的close不同，表明前复权需要重新计算
        #     #         if round(old, 2) != round(new, 2):
        #     #             # 删掉重新获取
        #     #             self.session.query(self.data_schema).filter(self.data_schema.entity_id == entity.id).delete()
        #     #             start = "2005-01-01"

        if not start:
            start = "2005-01-01"
        if not end:
            end = current_date()

        # df = qmt_quote.get_kdata(
        #     entity_id=entity.id,
        #     start_timestamp=start,
        #     end_timestamp=end,
        #     adjust_type=self.adjust_type,
        #     level=self.level,
        #     download_history=False,
        # )
        # if pd_is_not_null(df):
        #     df["entity_id"] = entity.id
        #     df["timestamp"] = pd.to_datetime(df.index)
        #     df["id"] = df.apply(lambda row: f"{row['entity_id']}_{to_time_str(row['timestamp'])}", axis=1)
        #     df["provider"] = "qmt"
        #     df["level"] = self.level.value
        #     df["code"] = entity.code
        #     df["name"] = entity.name
        #     df.rename(columns={"amount": "turnover"}, inplace=True)
        #     df["change_pct"] = (df["close"] - df["preClose"]) / df["preClose"]
        #     df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)
        #
        # else:
        #     self.logger.info(f"no kdata for {entity.id}")


class QMTStockKdataRecorder(BaseQmtKdataRecorder):
    entity_schema = Stock
    data_schema = StockKdataCommon


if __name__ == "__main__":
    # Stock.record_data(provider="qmt")
    QMTStockKdataRecorder(entity_id="stock_sz_301611", adjust_type=AdjustType.qfq).run()


# the __all__ is generated
__all__ = ["BaseQmtKdataRecorder", "QMTStockKdataRecorder"]
