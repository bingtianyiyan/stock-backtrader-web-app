# 轮动策略
import streamlit as st
import akshare as ak
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


# ====================== 函数定义部分 ======================

def calculate_technical_indicators(data, symbol_dict, lookback_days=20):
    """
    计算技术指标：收益率、涨跌幅等
    """
    for name in symbol_dict.keys():
        # 计算n/20日收益率
        data[f'收盘_{name}_{lookback_days}'] = data[f'收盘_{name}'].pct_change(lookback_days)
        data[f'收盘_{name}_pct'] = (data[f'收盘_{name}'] - data[f'收盘_{name}_{lookback_days}']) / data[f'收盘_{name}_{lookback_days}']

        # 计算每日涨跌幅
        data[f'收盘_{name}_1'] = data[f'收盘_{name}'].pct_change(1)
        data[f'涨跌幅_{name}'] = (data[f'收盘_{name}'] - data[f'收盘_{name}_1']) / data[f'收盘_{name}_1']
    return data

def select_stocks(data, symbol_dict):
    """
    执行选股逻辑，选择收益率最高的股票
    """
    pct_columns = [f'收盘_{name}_pct' for name in symbol_dict]
    pct_matrix = data[pct_columns].values
    max_indices = np.argmax(pct_matrix, axis=1)
    max_values = np.take_along_axis(pct_matrix, max_indices[:, None], axis=1).flatten()

    stocks = np.array(list(symbol_dict.keys()))
    data['下一日购买标的'] = np.where(
        max_values > 0,
        stocks[max_indices],
        None
    )
    return data

def calculate_performance_metrics(data):
    """
    计算绩效指标：最大回撤、年化收益率等
    """
    max_backup_list = []
    profit_ratio_list = []
    net_value_list = data['累计净值'].values.tolist()

    for i in range(len(net_value_list)):
        # 年化收益率
        profit_ratio_list.append((net_value_list[i] - 1) * 365 / (i + 1))

        # 最大回撤
        if i == 0:
            max_backup_list.append(abs(net_value_list[i] - 1))
        else:
            tmp_value = (max(net_value_list[:i]) - net_value_list[i]) / max(net_value_list[:i])
            max_backup_list.append(tmp_value)

    data['最大回撤'] = max_backup_list
    data['年化收益率'] = profit_ratio_list
    return data

def backtest_strategy(data, symbol_dict):
    """
    执行回测逻辑，计算策略收益
    """
    data = data.copy()
    data.index = range(data.shape[0])
    data['当日购买标的'] = data['下一日购买标的'].shift(1)
    buy_etf_list = data['当日购买标的'].values.tolist()
    profit_list = [0]  # 初始收益为0

    for i in range(1, len(buy_etf_list)):
        # 情况1：当日无买入信号
        if buy_etf_list[i] is None:
            profit_list.append(0)
        # 情况2：换仓（前一日无持仓或切换股票）
        elif buy_etf_list[i - 1] is None or buy_etf_list[i - 1] != buy_etf_list[i]:
            open_price = data.loc[i, f'开盘_{buy_etf_list[i]}']
            close_price = data.loc[i, f'收盘_{buy_etf_list[i]}']
            profit_list.append((close_price - open_price) / open_price)  # 当日买入的收益率
        else: # 情况3：持有上一日的股票
            close_price_pre = data.loc[i - 1, f'收盘_{buy_etf_list[i]}']
            close_price = data.loc[i, f'收盘_{buy_etf_list[i]}']
            profit_list.append((close_price - close_price_pre) / close_price_pre) # 持有收益率

    data['购买标的涨跌幅'] = profit_list
    data['净值'] = 1 + data['购买标的涨跌幅']
    data['累计净值'] = data['净值'].cumprod()
    return data


def display_results(data, symbol_dict):
    """
    展示回测结果和可视化图表
    """
    # 关键指标
    col1, col2 = st.columns(2)
    with col1:
        st.metric("策略最终净值", f"{data['累计净值'].iloc[-1]:.2f}")
        st.metric("最大回撤", f"{data['最大回撤'].max() * 100:.1f}%")
    with col2:
        st.metric("年化收益率", f"{data['年化收益率'].iloc[-1] * 100:.1f}%")
        st.metric("交易天数", len(data))

    # 净值曲线图
    st.subheader("策略净值曲线")
    fig = px.line(data, x='日期', y='累计净值', title="轮动策略净值曲线")
    st.plotly_chart(fig, use_container_width=True)

    # 各指数净值对比
    st.subheader("各指数表现对比")
    compare_df = pd.DataFrame({'日期': data['日期']})
    for name in symbol_dict.keys():
        compare_df[name] = data[f'收盘_{name}'] / data[f'收盘_{name}'].iloc[0]

    fig2 = px.line(
        compare_df.melt(id_vars='日期', var_name='指数', value_name='净值'),
        x='日期', y='净值', color='指数',
        title="各指数标准化净值对比"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 持仓分布
    st.subheader("持仓分布")
    holdings = data['当日购买标的'].value_counts().reset_index()
    holdings.columns = ['指数', '持仓天数']
    fig3 = px.pie(holdings, values='持仓天数', names='指数', title="各指数持仓天数占比")
    st.plotly_chart(fig3, use_container_width=True)

    # 原始数据展示
    st.subheader("详细数据")
    st.dataframe(data.sort_values('日期', ascending=False), height=300)

    # 数据下载
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下载回测数据(CSV)",
        data=csv,
        file_name='轮动策略回测数据.csv',
        mime="text/csv"
    )



