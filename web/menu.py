import streamlit as st

from frames.sidebar import dynamic_multi_level_menu
from web.backtraderpage import stockAnalysis
from web.etfpage import show_etf_page, show_etf_list, show_rotation_strategy_page
from web.stockpage import show_stock_page, show_rsi_page


#设置菜单
def set_menu():
    menu_title = "Tiny系统"
    #一级菜单
    menu_options = ["首页", "ETF数据","Stock数据","回测分析"]
    menu_icons= ["house", "bar-chart", "bar-chart", "bar-chart"]
    # 二级菜单映射
    submenus = {
        "首页":None,
        "ETF数据": ["数据概览", "回测分析"],
        "Stock数据": ["数据概览", "回测分析"],
        "回测分析": None
    }
    submenu_icons = {
        "ETF数据": ["clipboard-data", "clipboard-data"],
        "Stock数据": ["clipboard-data", "clipboard-data"]
    }
    # ===== 生成菜单 =====
    selected_primary, selected_secondary = dynamic_multi_level_menu(
        menu_title=menu_title,
        primary_options=menu_options,
        primary_icons=menu_icons,
        submenu_dict=submenus,
        submenu_icons=submenu_icons
    )

    # ===== 显示对应内容 =====
    st.title(f"{selected_primary} > {selected_secondary}" if selected_secondary else selected_primary)

    if selected_primary ==  menu_options[0]:
        home_page()
    elif selected_primary == menu_options[1]:
         etf_page(selected_secondary,menu_options,submenus)
    elif selected_primary == menu_options[2]:
         stock_page(selected_secondary,menu_options,submenus)
    elif selected_primary == menu_options[3]:
            back_trader_page()


    # selected = sidebar_navigation(menu_title, menu_options,menu_icons,submenu_icons)
    # # 根据选中的菜单显示不同页面
    # if selected == menu_options[0]:
    #     home_page()
    # elif selected == menu_options[1]:
    #     etf_page()
    # elif selected == menu_options[2]:
    #     stock_page()
    # elif selected == menu_options[3]:
    #     back_trader_page()
    # # 更新当前页面状态
    # st.session_state.current_page = selected

# 定义不同页面的内容
def home_page():
    st.title("🏠 首页")
    st.write("这里是首页内容...")

def etf_page(selected_secondary,menu_options,submenus):
    #st.title("📊 ETF数据")
    if selected_secondary == submenus[menu_options[1]][0]:
        show_etf_list()
    elif selected_secondary == submenus[menu_options[1]][1]:
        show_rotation_strategy_page()

def stock_page(selected_secondary,menu_options,submenus):
    if selected_secondary == submenus[menu_options[1]][0]:
        st.write("这里是内容...")
    elif selected_secondary == submenus[menu_options[2]][1]:
        show_rsi_page()
    #st.title("📈 Stock数据")
    #show_stock_page()

def back_trader_page():
    st.title("📈 回测数据")
    stockAnalysis()
    