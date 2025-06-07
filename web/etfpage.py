import streamlit as st

from service.etfservice import get_etf_data
from utils.streamlit_utils import download_csv_button, color_negative_red


# etf页面内容
def show_etf_page():
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


