import streamlit as st

from frames.sidebar import sidebar_navigation
from web.backtraderpage import stockAnalysis
from web.etfpage import show_etf_page


#设置菜单
def set_menu():
    menu_title = "Tiny系统"
    options = ["首页", "ETF数据","Stock数据","回测分析"]
    menu_icon= ["house", "bar-chart", "bar-chart", "bar-chart"]
    selected = sidebar_navigation(menu_title, options,menu_icon)
    # 根据选中的菜单显示不同页面
    if selected == options[0]:
        home_page()
    elif selected == options[1]:
        etf_page()
    elif selected == options[2]:
        stock_page()
    elif selected == options[3]:
        back_trader_page()
    # 更新当前页面状态
    st.session_state.current_page = selected

# 定义不同页面的内容
def home_page():
    st.title("🏠 首页")
    st.write("这里是首页内容...")

def etf_page():
    #st.title("📊 ETF数据")
    show_etf_page()

def stock_page():
    st.title("📈 Stock数据")
    st.write("这里是设置页面...")

def back_trader_page():
    st.title("📈 回测数据")
    stockAnalysis()