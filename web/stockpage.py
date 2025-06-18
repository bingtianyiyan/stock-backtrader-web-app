import os
import re
import streamlit as st
import akshare as ak
import pandas as pd

from internal.domain.schemas import Stock
from internal.service.akshareservice import get_stock_name
from internal.pkg.strategy.rsi import backtest_rsi_strategy, plot_results

# 页面内容
def show_stock_page():
    show_rsi_page()

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
