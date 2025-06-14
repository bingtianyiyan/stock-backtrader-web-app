# -*- coding: utf-8 -*-

from core.contract.api import df_to_db
from core.contract.recorder import Recorder
from core.domain import Index
from core.recorders.em import em_api


class EMIndexRecorder(Recorder):
    provider = "em"
    data_schema = Index

    def run(self):
        df = em_api.get_tradable_list(entity_type="index")
        self.logger.info(df)
        df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)


if __name__ == "__main__":
    recorder = EMIndexRecorder()
    recorder.run()


# the __all__ is generated
__all__ = ["EMIndexRecorder"]
