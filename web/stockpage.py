import os
import re
import streamlit as st
import akshare as ak
import pandas as pd

from core.contract import zvt_context, IntervalLevel, Mixin
from core.contract.api import get_entities, get_schema_by_name, get_schema_columns
from core.contract.drawer import StackedDrawer
from core.trader.trader_info_api import get_order_securities, OrderReader, get_trader_info, AccountStatsReader
from core.utils.pd_utils import pd_is_not_null
from internal.domain.schemas import Stock
from internal.service.akshareservice import get_stock_name
from internal.pkg.strategy.rsi import backtest_rsi_strategy, plot_results

# 页面内容
def show_stock_page():
    show_rsi_page()
    show_trader_page()

#Rsi
def show_rsi_page():
    st.header("🏛️ 股票RSI策略回测系统")
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    st.header("参数设置")
    stock_code = st.text_input("股票代码")
    if len(stock_code) == 0:
        return
    stock_code = re.sub(r"^[sSzZ][hH]?", "", stock_code, flags=re.IGNORECASE)
    stock_name = get_stock_name(stock_code)
    if len(stock_name) == 0:
        return

    stock_info = Stock(
        code=stock_code,
        name=stock_name,
        market="",
        sector="",
        listing_date=""
    )

    start_date = st.date_input("开始日期", pd.to_datetime("2024-01-01"))
    end_date = st.date_input("结束日期", pd.to_datetime("2025-06-30"))
    initial_capital = st.number_input("初始资金(元)", 100000, 10000000, 100000)
    trade_volume = st.number_input("每笔交易股数", 100, 10000, 100)
    rsi_period = st.slider("RSI周期", 5, 30, 14)
    overbought = st.slider("超买线", 50, 90, 70)
    oversold = st.slider("超卖线", 10, 50, 30)

    if st.button("开始回测"):
        with st.spinner("正在执行回测..."):
            try:
                # 获取数据
                stock_df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="hfq"
                )
                stock_df.index = pd.to_datetime(stock_df['日期'])

                # 执行回测
                result_df = backtest_rsi_strategy(
                    stock_df,
                    initial_capital=initial_capital,
                    trade_volume=trade_volume,
                    rsi_period=rsi_period,
                    overbought=overbought,
                    oversold=oversold
                )
                # 显示结果
                st.session_state.result_df = result_df
                st.session_state.stock_info = stock_info
                st.success("回测完成！")
            except Exception as e:
                st.error(f"回测失败: {str(e)}")

    # 主显示区域
    if 'result_df' in st.session_state:
        result_df = st.session_state.result_df
        stock_info = st.session_state.stock_info

        # 绩效分析
        final_asset = result_df['total_asset'].iloc[-1]
        total_return = (final_asset - initial_capital) / initial_capital
        annualized_return = (1 + total_return) ** (252 / len(result_df)) - 1
        trade_records = result_df[result_df['signal'] != 0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("初始资金", f"¥{initial_capital:,.2f}")
            st.metric("最终总资产", f"¥{final_asset:,.2f}",
                      f"{total_return:.2%}")
        with col2:
            st.metric("年化收益率", f"{annualized_return:.2%}")
            st.metric("交易次数", len(trade_records))
        with col3:
            st.metric("最终持仓", f"{result_df['position'].iloc[-1]:,}股")
            st.metric("股票市值", f"¥{result_df['stock_value'].iloc[-1]:,.2f}")

        # 显示数据和图表
        st.subheader("回测结果数据")
        st.dataframe(result_df.tail(10), use_container_width=True)

        st.subheader("交易记录")
        st.dataframe(trade_records, use_container_width=True)

        st.subheader("可视化分析")
        plot_results(result_df, stock_info.name)

        # 下载按钮
        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载回测数据(CSV)",
            data=csv,
            file_name=f"{stock_info.name}_RSI回测.csv",
            mime="text/csv"
        )
    else:
        st.info("请在左侧设置参数并点击【开始回测】")

def order_type_flag(order_type):
    if order_type == "order_long" or order_type == "order_close_short":
        return "B"
    else:
        return "S"


def order_type_color(order_type):
    if order_type == "order_long" or order_type == "order_close_short":
        return "#ec0000"
    else:
        return "#00da3c"


def load_traders():
    st.session_state.traders = get_trader_info(return_type="domain")
    st.session_state.account_readers = []
    st.session_state.order_readers = []
    for trader in st.session_state.traders:
        st.session_state.account_readers.append(
            AccountStatsReader(level=trader.level, trader_names=[trader.trader_name]))
        st.session_state.order_readers.append(
            OrderReader(start_timestamp=trader.start_timestamp, level=trader.level, trader_names=[trader.trader_name])
        )
    st.session_state.trader_names = [item.trader_name for item in st.session_state.traders]


def setup_sidebar_controls():
    st.header("Trader Selection")
    trader_index = st.selectbox(
        "Select trader:",
        options=list(range(len(st.session_state.trader_names))),
        format_func=lambda x: st.session_state.trader_names[x]
    )

    st.header("Entity Selection")
    entity_type = st.selectbox(
        "Select entity type:",
        options=list(zvt_context.tradable_schema_map.keys()),
        index=0
    )

    providers = zvt_context.tradable_schema_map.get(entity_type).providers
    entity_provider = st.selectbox(
        "Select entity provider:",
        options=providers
    )

    entity_options = []
    if trader_index is not None:
        entity_ids = get_order_securities(trader_name=st.session_state.trader_names[trader_index])
        entity_df = get_entities(
            provider=entity_provider,
            entity_type=entity_type,
            entity_ids=entity_ids,
            columns=["entity_id", "code", "name"],
            index="entity_id"
        )
        entity_options = [
            {"label": f'{entity_id}({entity["name"]})', "value": entity_id}
            for entity_id, entity in entity_df.iterrows()
        ]
    else:
        entity_df = get_entities(
            provider=entity_provider,
            entity_type=entity_type,
            columns=["entity_id", "code", "name"],
            index="entity_id"
        )
        entity_options = [
            {"label": f'{entity_id}({entity["name"]})', "value": entity_id}
            for entity_id, entity in entity_df.iterrows()
        ]

    entity = st.selectbox(
        "Select entity:",
        options=[opt["value"] for opt in entity_options],
        format_func=lambda x: next(opt["label"] for opt in entity_options if opt["value"] == x)
    )

    st.header("Level Selection")

    # 创建正确的选项列表 - 使用元组(value, label)
    level_options = [
        (IntervalLevel.LEVEL_1WEEK.value, f"Weekly ({IntervalLevel.LEVEL_1WEEK.value})"),
        (IntervalLevel.LEVEL_1DAY.value, f"Daily ({IntervalLevel.LEVEL_1DAY.value})")
    ]

    # 确保默认值在选项中
    default_level = IntervalLevel.LEVEL_1DAY.value
    default_levels = [default_level] if default_level in [opt[0] for opt in level_options] else [level_options[0][0]]

    levels = st.multiselect(
        "Select levels:",
        options=[opt[0] for opt in level_options],  # 只传递值列表
        default=default_levels,
        format_func=lambda x: dict(level_options).get(x, x)  # 使用字典查找显示标签
    )

    st.header("Factor Selection")
    factor = st.selectbox(
        "Select factor:",
        options=list(zvt_context.factor_cls_registry.keys()),
        index=list(zvt_context.factor_cls_registry.keys()).index(
            "TechnicalFactor") if "TechnicalFactor" in zvt_context.factor_cls_registry else 0
    )

    st.header("Additional Data")
    show_related_data = st.checkbox("Show related data in sub graph", value=True)
    # Initialize schema_name and columns with default values
    schema_name = None
    columns = []
    if entity_type is not None:
        if show_related_data:
            schemas = zvt_context.entity_map_schemas.get(entity_type)
        else:
            schemas = zvt_context.schemas
        schema_options = [schema.__name__ for schema in schemas]
        schema_name = st.selectbox("Select schema:", options=schema_options)

        if schema_name:
            schema = get_schema_by_name(name=schema_name)
            cols = get_schema_columns(schema=schema)
            columns = st.multiselect("Select properties:", options=cols)

    return trader_index, entity_type, entity, levels, factor, schema_name, columns


def get_account_stats_figure(account_stats_reader):
    pass


def display_main_content(trader_index, entity_type, entity, levels, factor, schema_name, columns):
    st.title("Trader Analysis")

    if trader_index is not None:
        st.subheader(f"Trader: {st.session_state.trader_names[trader_index]}")
        account_stats_fig = get_account_stats_figure(
            account_stats_reader=st.session_state.account_readers[trader_index])
        st.plotly_chart(account_stats_fig, use_container_width=True)

    if factor and entity_type and entity and levels:
        st.subheader(f"Factor Analysis: {factor}")

        sub_df = None
        if columns:
            columns = list(columns) + ["entity_id", "timestamp"]
            schema: Mixin = get_schema_by_name(name=schema_name)
            sub_df = schema.query_data(entity_id=entity, columns=columns)

        annotation_df = None
        if trader_index is not None:
            order_reader = st.session_state.order_readers[trader_index]
            annotation_df = order_reader.data_df.copy()
            annotation_df = annotation_df[annotation_df.entity_id == entity].copy()
            if pd_is_not_null(annotation_df):
                annotation_df["value"] = annotation_df["order_price"]
                annotation_df["flag"] = annotation_df["order_type"].apply(lambda x: order_type_flag(x))
                annotation_df["color"] = annotation_df["order_type"].apply(lambda x: order_type_color(x))

        if type(levels) is list and len(levels) >= 2:
            levels.sort()
            drawers = []
            for level in levels:
                drawers.append(
                    zvt_context.factor_cls_registry[factor](
                        entity_schema=zvt_context.tradable_schema_map[entity_type],
                        level=level,
                        entity_ids=[entity]
                    ).drawer()
                )
            stacked = StackedDrawer(*drawers)
            fig = stacked.draw_kline(show=False, height=900)
        else:
            level = levels[0] if isinstance(levels, list) else levels
            drawer = zvt_context.factor_cls_registry[factor](
                entity_schema=zvt_context.tradable_schema_map[entity_type],
                level=level,
                entity_ids=[entity],
                need_persist=False
            ).drawer()

            if pd_is_not_null(sub_df):
                drawer.add_sub_df(sub_df)
            if pd_is_not_null(annotation_df):
                drawer.annotation_df = annotation_df

            fig = drawer.draw_kline(show=False, height=800)

        st.plotly_chart(fig, use_container_width=True)


def show_trader_page():
    st.header("🏛️ 股票交易测试")
    # Initialize session state
    if 'traders' not in st.session_state:
        st.session_state.traders = []
    if 'trader_names' not in st.session_state:
        st.session_state.trader_names = []
    if 'account_readers' not in st.session_state:
        st.session_state.account_readers = []
    if 'order_readers' not in st.session_state:
        st.session_state.order_readers = []

    # Load traders data if not already loaded
    if not st.session_state.traders:
        load_traders()

    # Setup controls and get their values
    controls = setup_sidebar_controls()

    # Display main content
    display_main_content(*controls)