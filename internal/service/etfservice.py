import akshare as ak
import pandas as pd
import streamlit as st

# etf数据获取函数
@st.cache_data(ttl=3600)
def get_etf_data():
    try:
        df = ak.fund_etf_spot_em()
        # 数据清洗和转换
        if not df.empty:
            # 数据清洗和格式化
            df = df.rename(columns={
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_percent',
                '成交量': 'volume',
                '成交额': 'turnover'
            })

            # 转换数据类型
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df['change_percent'] = df['change_percent'].astype(str).str.replace('%', '').astype(
                float)  # df['change_percent'].str.replace('%', '').astype(float)
            df['volume'] = df['volume'].astype(
                float) * 100  # pd.to_numeric(df['volume'], errors='coerce') * 100  # 转换为股数
            df['turnover'] = pd.to_numeric(df['turnover'], errors='coerce') * 10000  # 转换为元

            return df.dropna()
        return df
    except Exception as e:
        st.error(f"ETF数据获取失败: {str(e)}")
        return pd.DataFrame()

#获取多个指数的历史数据并合并
def get_zh_history(symbol_dict, start_date, end_date):
    """
    获取多个指数的历史数据并合并
    """
    index_his = None
    for name, code in symbol_dict.items():
        try:
            index_his_tmp = ak.index_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date
            )
            index_his_tmp = index_his_tmp[['日期', '开盘', '收盘']]
            index_his_tmp.columns = ['日期', f'开盘_{name}', f'收盘_{name}']

            if index_his is None:
                index_his = index_his_tmp
            else:
                index_his = index_his.merge(index_his_tmp, on=['日期'], how='left')
        except Exception as e:
            st.error(f"获取{name}({code})数据失败: {str(e)}")
            continue

    if index_his is not None:
        index_his = index_his.sort_values(['日期'])
    return index_his
