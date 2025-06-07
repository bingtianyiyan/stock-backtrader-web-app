import datetime

from service.backtraderservice import gen_stock_df, run_backtrader
from utils.load import load_strategy
from models.schemas import AkshareParams, BacktraderParams
import streamlit as st
from streamlit_echarts import st_pyecharts

from charts import draw_pro_kline, draw_result_bar
from utils.logs import logger
from models.schemas import StrategyBase

strategy_dict = load_strategy("./config/strategy.yaml")

def stockAnalysis():
    ak_params = akshare_selector_ui()
    bt_params = backtrader_selector_ui()
    if ak_params.symbol:
        stock_df = gen_stock_df(ak_params)
        if stock_df.empty:
            st.error("Get stock data failed!")
            return

        st.subheader("Kline")
        kline = draw_pro_kline(stock_df)
        st_pyecharts(kline, height="500px")

        st.subheader("Strategy")
        name = st.selectbox("strategy", list(strategy_dict.keys()))
        submitted, params = params_selector_ui(strategy_dict[name])
        if submitted:
            logger.info(f"akshare: {ak_params}")
            logger.info(f"backtrader: {bt_params}")
            stock_df = stock_df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                }
            )
            strategy = StrategyBase(name=name, params=params)
            par_df = run_backtrader(stock_df, strategy, bt_params)
            st.dataframe(par_df.style.highlight_max(subset=par_df.columns[-3:]))
            bar = draw_result_bar(par_df)
            st_pyecharts(bar, height="500px")


def akshare_selector_ui() -> AkshareParams:
    """akshare params

    :return: AkshareParams
    """
    st.markdown("# Akshare Config")
    symbol = st.text_input("symbol")
    period = st.selectbox("period", ("daily", "weekly", "monthly"))
    start_date = st.date_input("start date", datetime.date(1970, 1, 1))
    start_date = start_date.strftime("%Y%m%d")
    end_date = st.date_input("end date", datetime.datetime.today())
    end_date = end_date.strftime("%Y%m%d")
    adjust = st.selectbox("adjust", ("qfq", "hfq", ""))
    return AkshareParams(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )


def backtrader_selector_ui() -> BacktraderParams:
    """backtrader params

    :return: BacktraderParams
    """
    st.markdown("# BackTrader Config")
    start_date = st.date_input("backtrader start date", datetime.date(2000, 1, 1))
    end_date = st.date_input("backtrader end date", datetime.datetime.today())
    start_cash = st.number_input("start cash", min_value=0, value=100000, step=10000)
    commission_fee = st.number_input("commission fee", min_value=0.0, max_value=1.0, value=0.001, step=0.0001)
    stake = st.number_input("stake", min_value=0, value=100, step=10)
    return BacktraderParams(
        start_date=start_date,
        end_date=end_date,
        start_cash=start_cash,
        commission_fee=commission_fee,
        stake=stake,
    )