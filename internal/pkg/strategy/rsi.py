# Rsi策略
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import platform


# 设置中文字体
def set_chinese_font():
    """智能设置中文字体（自动适配不同操作系统）"""
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    system = platform.system()
    try:
        if system == 'Windows':
            plt.rcParams['font.family'] = 'Microsoft YaHei'
            font_path = 'C:/Windows/Fonts/msyh.ttc'
        elif system == 'Darwin':
            plt.rcParams['font.family'] = 'PingFang SC'
            font_path = '/System/Library/Fonts/PingFang.ttc'
        else:
            plt.rcParams['font.family'] = 'WenQuanYi Micro Hei'
            font_path = 'usr/share/fonts/truetype/wqy/wqy-microhei.ttc'

        return FontProperties(fname=font_path)
    except:
        plt.rcParams['font.family'] = 'sans-serif'
        return FontProperties()


font_prop = set_chinese_font()


# RSI计算函数
def calculate_rsi(data, period=14):
    data = data.copy()
    delta = data['收盘'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['超买线'] = 70
    data['超卖线'] = 30
    return data


# 回测策略
def backtest_rsi_strategy(data, initial_capital=100000, trade_volume=100, commission_rate=0.0003, rsi_period=14,
                          overbought=70, oversold=30):
    data = data.copy()
    data['signal'] = 0
    data['position'] = 0
    data['cash'] = initial_capital
    data['stock_value'] = 0.0
    data['total_asset'] = initial_capital
    data['trade_amount'] = 0.0

    data = calculate_rsi(data, rsi_period)
    float_cols = ['cash', 'stock_value', 'total_asset']
    data[float_cols] = data[float_cols].astype('float64')

    for i in range(1, len(data)):
        prev_row = data.iloc[i - 1]
        current_row = data.iloc[i]

        data.iloc[i, data.columns.get_loc('position')] = prev_row['position']
        data.iloc[i, data.columns.get_loc('cash')] = prev_row['cash']
        data.iloc[i, data.columns.get_loc('signal')] = 0
        data.iloc[i, data.columns.get_loc('trade_amount')] = 0

        # 买入信号
        if i >= 2 and prev_row['RSI'] > oversold and data.iloc[i - 2]['RSI'] <= oversold:
            current_open = current_row['开盘']
            buy_cost = current_open * trade_volume * (1 + commission_rate)
            if prev_row['cash'] >= buy_cost:
                data.iloc[i, data.columns.get_loc('signal')] = 1
                data.iloc[i, data.columns.get_loc('position')] = prev_row['position'] + trade_volume
                data.iloc[i, data.columns.get_loc('cash')] = float(prev_row['cash'] - buy_cost)
                data.iloc[i, data.columns.get_loc('trade_amount')] = -buy_cost

        # 卖出信号
        elif i >= 2 and prev_row['RSI'] < overbought and data.iloc[i - 2]['RSI'] >= overbought:
            if prev_row['position'] >= trade_volume:
                current_open = current_row['开盘']
                sell_revenue = current_open * trade_volume * (1 - commission_rate)
                data.iloc[i, data.columns.get_loc('signal')] = -1
                data.iloc[i, data.columns.get_loc('position')] = prev_row['position'] - trade_volume
                data.iloc[i, data.columns.get_loc('cash')] = prev_row['cash'] + sell_revenue
                data.iloc[i, data.columns.get_loc('trade_amount')] = sell_revenue

        # 计算资产
        current_close = current_row['收盘']
        data.iloc[i, data.columns.get_loc('stock_value')] = data.iloc[i]['position'] * current_close
        data.iloc[i, data.columns.get_loc('total_asset')] = data.iloc[i]['cash'] + data.iloc[i]['stock_value']

    return data


# 绘制图表
def plot_results(result_df, stock_name):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

    # 价格和RSI
    ax1.plot(result_df['收盘'], label='收盘价', color='b')
    ax1.set_title(f'{stock_name} RSI策略回测', fontproperties=font_prop)
    ax1_rsi = ax1.twinx()
    ax1_rsi.plot(result_df['RSI'], label='RSI', color='orange')
    ax1_rsi.axhline(70, color='r', linestyle='--')
    ax1_rsi.axhline(30, color='g', linestyle='--')
    ax1_rsi.set_ylim(0, 100)

    # 买卖信号
    ax2.plot(result_df['收盘'], label='收盘价', color='b', alpha=0.3)
    buy_signals = result_df[result_df['signal'] == 1]
    sell_signals = result_df[result_df['signal'] == -1]
    ax2.scatter(buy_signals.index, buy_signals['收盘'], label='买入', marker='^', color='r')
    ax2.scatter(sell_signals.index, sell_signals['收盘'], label='卖出', marker='v', color='g')
    ax2.legend(prop=font_prop)

    # 资产变化
    ax3.plot(result_df['total_asset'], label='总资产', color='purple')
    ax3.plot(result_df['stock_value'], label='股票市值', color='g', linestyle='--')
    ax3.plot(result_df['cash'], label='现金', color='b', linestyle=':')
    ax3.legend(prop=font_prop)

    plt.tight_layout()
    st.pyplot(fig)