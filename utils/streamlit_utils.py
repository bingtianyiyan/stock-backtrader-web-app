import streamlit as st

# 下载csv
def download_csv_button(filename,df = None):
    # 添加下载按钮
    st.download_button(
        label="下载CSV数据",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f'{filename}.csv',
        mime='text/csv'
    )

#更美观的涨跌颜色显示
def color_negative_red(val):
    if isinstance(val, str) and '-' in val:
        return 'color: red'
    elif isinstance(val, str) and '+' in val:
        return 'color: green'
    return ''