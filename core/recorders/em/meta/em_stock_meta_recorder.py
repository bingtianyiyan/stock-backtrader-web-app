# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import text

from core.contract import Exchange
from core.contract.api import df_to_db
from core.contract.recorder import Recorder
from core.domain import Stock
from core.recorders.em import em_api
from core.utils.pd_utils import pd_is_not_null


class EMStockRecorder(Recorder):
    provider = "em"
    data_schema = Stock

    def run(self):
        for exchange in [Exchange.sh, Exchange.sz, Exchange.bj]:
            df = em_api.get_tradable_list(entity_type="stock", exchange=exchange)
            # df_delist = df[df["name"].str.contains("退")]
            if pd_is_not_null(df):
                for item in df[["id", "name"]].values.tolist():
                    sql = text('UPDATE stock SET name = :name WHERE id = :id')
                    self.session.execute(sql,{'name': item[1], 'id': item[0]})
                    self.session.commit()
            self.logger.info(df)
            df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)


if __name__ == "__main__":
    recorder = EMStockRecorder()
    recorder.run()


# the __all__ is generated
__all__ = ["EMStockRecorder"]
