# -*- coding: utf-8 -*-
import pandas as pd

from core.api.portfolio import get_etf_stocks
from core.contract.api import df_to_db
from core.contract.recorder import TimeSeriesDataRecorder
from core.domain import StockValuation, Etf, EtfValuation
from core.utils.pd_utils import pd_is_not_null
from core.utils.time_utils import now_pd_timestamp


class JqChinaEtfValuationRecorder(TimeSeriesDataRecorder):
    entity_provider = "joinquant"
    entity_schema = Etf

    # 数据来自jq
    provider = "joinquant"

    data_schema = EtfValuation

    def record(self, entity, start, end, size, timestamps):
        if not end:
            end = now_pd_timestamp()

        date_range = pd.date_range(start=start, end=end, freq="1D").tolist()
        for date in date_range:
            # etf包含的个股和比例
            etf_stock_df = get_etf_stocks(code=entity.code, timestamp=date, provider=self.provider)

            if pd_is_not_null(etf_stock_df):
                all_pct = etf_stock_df["proportion"].sum()

                if all_pct >= 1.2 or all_pct <= 0.8:
                    self.logger.error(f"ignore etf:{entity.id}  date:{date} proportion sum:{all_pct}")
                    break

                etf_stock_df.set_index("stock_id", inplace=True)

                # 个股的估值数据
                stock_valuation_df = StockValuation.query_data(
                    entity_ids=etf_stock_df.index.to_list(),
                    filters=[StockValuation.timestamp == date],
                    index="entity_id",
                )

                if pd_is_not_null(stock_valuation_df):
                    stock_count = len(etf_stock_df)
                    valuation_count = len(stock_valuation_df)

                    self.logger.info(
                        f"etf:{entity.id} date:{date} stock count: {stock_count}," f"valuation count:{valuation_count}"
                    )

                    pct = abs(stock_count - valuation_count) / stock_count

                    if pct >= 0.2:
                        self.logger.error(f"ignore etf:{entity.id}  date:{date} pct:{pct}")
                        break

                    se = pd.Series(
                        {
                            "id": "{}_{}".format(entity.id, date),
                            "entity_id": entity.id,
                            "timestamp": date,
                            "code": entity.code,
                            "name": entity.name,
                        }
                    )
                    for col in ["pe", "pe_ttm", "pb", "ps", "pcf"]:
                        # PE=P/E
                        # 这里的算法为：将其价格都设为PE,那么Earning为1(亏钱为-1)，结果为 总价格(PE)/总Earning

                        value = 0
                        price = 0

                        # 权重估值
                        positive_df = stock_valuation_df[[col]][stock_valuation_df[col] > 0]
                        positive_df["count"] = 1
                        positive_df = positive_df.multiply(etf_stock_df["proportion"], axis="index")
                        if pd_is_not_null(positive_df):
                            value = positive_df["count"].sum()
                            price = positive_df[col].sum()

                        negative_df = stock_valuation_df[[col]][stock_valuation_df[col] < 0]
                        if pd_is_not_null(negative_df):
                            negative_df["count"] = 1
                            negative_df = negative_df.multiply(etf_stock_df["proportion"], axis="index")
                            value = value - negative_df["count"].sum()
                            price = price + negative_df[col].sum()

                        se[f"{col}1"] = price / value

                        # 简单算术平均估值
                        positive_df = stock_valuation_df[col][stock_valuation_df[col] > 0]
                        positive_count = len(positive_df)

                        negative_df = stock_valuation_df[col][stock_valuation_df[col] < 0]
                        negative_count = len(negative_df)

                        value = positive_count - negative_count
                        price = positive_df.sum() + abs(negative_df.sum())

                        se[col] = price / value
                    df = se.to_frame().T

                    self.logger.info(df)

                    df_to_db(
                        df=df, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update
                    )

        return None


if __name__ == "__main__":
    # 上证50
    JqChinaEtfValuationRecorder(codes=["512290"]).run()


# the __all__ is generated
__all__ = ["JqChinaEtfValuationRecorder"]
