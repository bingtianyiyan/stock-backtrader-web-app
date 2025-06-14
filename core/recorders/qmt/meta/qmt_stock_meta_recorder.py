# -*- coding: utf-8 -*-

# from core.broker.qmt import qmt_quote
from core.contract.api import df_to_db
from core.contract.recorder import Recorder
from core.domain import Stock


class QMTStockRecorder(Recorder):
    provider = "qmt"
    data_schema = Stock

    def run(self):
        print("QMTStockRecorder")
        # df = qmt_quote.get_entity_list()
        # self.logger.info(df.tail())
        # df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=True)


if __name__ == "__main__":
    recorder = QMTStockRecorder()
    recorder.run()


# the __all__ is generated
__all__ = ["QMTStockRecorder"]
