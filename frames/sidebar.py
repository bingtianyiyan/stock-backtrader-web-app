import datetime
import streamlit as st
from streamlit_option_menu import option_menu

#streamlit 整体页面数据
def page_config():
    # 页面配置
    st.set_page_config(
        page_title="金融数据看板",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # 自定义CSS样式
    st.markdown("""
    <style>
        /* 主标题样式 */
        .header-style {
            text-align: center;
            color: #2e86c1;
            margin-bottom: 10px;
        }
    
        /* 侧边栏导航样式 */
        .nav-item {
            display: block;
            padding: 0.5rem 1rem;
            margin: 0.25rem 0;
            border-radius: 0.25rem;
            cursor: pointer;
            text-decoration: none !important;
        }
        .nav-item:hover {
            background-color: #f0f2f6;
        }
        .nav-item.active {
            background-color: #2e86c1;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    #sst.markdown('<h1 class="header-style">📊 金融数据综合分析看板</h1>', unsafe_allow_html=True)

    # 初始化session_state  固定先首页
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "首页"

# 菜单 侧边栏导航 - 兼容旧版Streamlit的实现
def sidebar_navigation(menu_title, options,menu_icon=None):
    with st.sidebar:
        selected = option_menu(
            menu_title,
            options,
            icons=menu_icon,
            menu_icon="cast",
            default_index=0,
        )
    st.markdown("""
     <style>
         [data-testid="stSidebar"] {
             width: 10px !important;
         }
         .st-option-menu {
             background-color: #f0f2f6;
         }
     </style>
     """, unsafe_allow_html=True)
    return selected
