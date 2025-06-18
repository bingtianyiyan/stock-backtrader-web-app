import datetime

import streamlit as st
import re
from datetime import datetime, timedelta
from internal.service.akshareservice import get_stock_name
from internal.service.etfservice import get_etf_data, get_zh_history
from internal.pkg.strategy.rotation import calculate_technical_indicators, calculate_performance_metrics, backtest_strategy, \
    select_stocks, display_results
from core.utils.streamlit_utils import download_csv_button, color_negative_red



# etf页面内容
def show_etf_page():
    show_etf_list()
    show_rotation_strategy_page()

# etf 列表
def show_etf_list():
    st.header("📈 ETF基金实时行情")

    with st.spinner('正在获取最新ETF数据...'):
        fund_etf_spot_em_df = get_etf_data()

    if not fund_etf_spot_em_df.empty:
        # 添加筛选功能
        col1, col2 = st.columns(2)
        with col1:
            selected_name = st.text_input('按基金名称筛选', '')
        with col2:
            sort_option = st.selectbox('排序方式', [
                '默认排序', '价格升序', '价格降序',
                '涨跌幅升序', '涨跌幅降序'
            ])

        # 应用筛选
        filtered_df = fund_etf_spot_em_df.copy() # 创建原始数据的副本
        if selected_name:
            filtered_df = filtered_df[filtered_df['name'].str.contains(selected_name)]

        # 应用排序
        if sort_option == '价格升序':
            filtered_df = filtered_df.sort_values('price')
        elif sort_option == '价格降序':
            filtered_df = filtered_df.sort_values('price', ascending=False)
        elif sort_option == '涨跌幅升序':
            filtered_df = filtered_df.sort_values('change_percent')
        elif sort_option == '涨跌幅降序':
            filtered_df = filtered_df.sort_values('change_percent', ascending=False)

        # 显示数据统计
        st.metric("ETF总数", len(filtered_df))

        # 使用AgGrid增强表格交互
        try:
            from st_aggrid import AgGrid
            AgGrid(
                filtered_df,
                height=600,
                width='100%',
                reload_data=False,
                columns_auto_size_mode='FIT_CONTENTS',
                enable_enterprise_modules=True
            )
        except ImportError:
            # 回退到标准表格
            st.dataframe(
                filtered_df.style.map(color_negative_red),
                height=600,
                use_container_width=True,
                hide_index=True
            )

        # 添加下载按钮
        download_csv_button("etf_data",filtered_df)
    else:
        st.warning("未获取到有效数据，请稍后重试或检查网络连接")

#轮动策略
def show_rotation_strategy_page():
    st.header("🏛️ 指数轮动策略回测系统")
    # 获取默认股票池
    default_pool = get_default_stock_pool()
    # 用户输入基金代码（逗号分隔）
    stock_code_list = st.text_input("指数代码（多个代码用逗号分隔,比如000001,000002）")

    if stock_code_list:  # 如果输入不为空
        codes = stock_code_list.split(",")  # 按逗号分割成列表
        for code in codes:
            code = code.strip()  # 去除前后空格（避免用户输入 " 123, 456 "）
            if code:  # 确保非空
                code = re.sub(r"^[sSzZ][hH]?", "", code, flags=re.IGNORECASE)
                name = get_stock_name(code)
                if len(name) > 0:
                   default_pool[name] = code  # 存入字典

    # 多选股票池
    selected_indices = st.multiselect(
        "选择股票指数",
        options=list(default_pool.keys()),
        default=list(default_pool.keys()))

    # 日期范围选择
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = st.date_input(
        "开始日期",
        value=datetime.now() - timedelta(days=365 * 5),
        max_value=datetime.now()
    ).strftime('%Y%m%d')

    end_date = st.date_input(
        "结束日期",
        value=datetime.now(),
        max_value=datetime.now()
    ).strftime('%Y%m%d')

    # 轮动周期
    lookback_days = st.slider("轮动周期(天)", 5, 60, 20)

    # 回测按钮
    run_backtest = st.button("执行回测分析")

    # 主内容区
    if run_backtest and selected_indices:
        st.divider()
        st.subheader("📊 回测结果")

        # 构建选股池
        select_pool = {k: default_pool[k] for k in selected_indices}

        # 显示加载状态
        with st.spinner("正在获取数据并计算策略..."):
                try:
                    # 1. 获取数据
                    index_data = get_zh_history(select_pool, start_date, end_date)

                    if index_data is None or len(index_data) == 0:
                        st.error("未能获取有效数据，请检查参数设置")
                        return

                    # 2. 计算技术指标
                    index_data = calculate_technical_indicators(index_data, select_pool, lookback_days)

                    # 3. 执行选股
                    index_data = select_stocks(index_data, select_pool)

                    # 4. 回测策略
                    result_data = backtest_strategy(index_data, select_pool)

                    # 5. 计算绩效指标
                    result_data = calculate_performance_metrics(result_data)

                    # 6. 展示结果
                    display_results(result_data, select_pool)

                except Exception as e:
                    st.error(f"回测过程中发生错误: {str(e)}")
                    st.exception(e)

    elif not selected_indices and run_backtest:
       st.warning("请至少选择一个股票指数进行分析！")
    else:
       st.info("请在左侧边栏设置参数并点击【执行回测分析】按钮")

def get_default_stock_pool():
    """返回默认股票池"""
    return {
        '上证50': '000016',
        '沪深300': '000300',
        '中证1000': '000852',
        '中证2000': '932000',
        '创业板指': '399006'
    }


