import datetime
import streamlit as st
from streamlit_option_menu import option_menu
from typing import Dict, List, Optional, Union

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
def sidebar_navigation(menu_title, menu_options, menu_icons=None,submenus=None,submenu_icons=None):
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
    with st.sidebar:
        selected_menu = option_menu(
            menu_title,
            menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
        # 动态显示二级菜单（仅当一级菜单有子项时）
        if selected_menu in submenus:
            selected_submenu = option_menu(
                menu_title=None,  # 隐藏二级菜单标题
                options=submenus[selected_menu],
                icons=submenu_icons,#["circle"] * len(submenus[selected_menu]),  # 二级菜单图标
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#3B4252"},
                    "nav-link": {"font-size": "13px", "padding": "5px 10px"},
                }
            )
            # ===== 主页面内容 =====
            st.title(f"{selected_menu} - {selected_submenu}" if selected_menu in submenus else selected_menu)
            return selected_submenu
    return selected_menu


def dynamic_multi_level_menu(
        menu_title,
        primary_options: List[str],
        primary_icons: List[str],
        submenu_dict: Dict[str, List[str]],
        submenu_icons: Optional[Dict[str, List[str]]] = None,
        styles: Optional[Dict] = None,
        key: str = "menu"
) -> tuple:
    """
    动态生成多级侧边栏菜单

    参数:
        primary_options: 一级菜单选项列表 (e.g. ["首页", "数据分析"])
        primary_icons: 一级菜单图标列表 (e.g. ["house", "bar-chart"])
        submenu_dict: 二级菜单映射字典 (e.g. {"数据分析": ["报表", "统计"]})
        submenu_icons: 二级菜单图标字典 (e.g. {"数据分析": ["file-earmark-bar-graph", "pie-chart"]})
        styles: 自定义样式字典
        key: 菜单唯一标识（用于session_state）

    返回:
        (selected_primary, selected_secondary) 当前选中的菜单项
    """
    # ===== CSS样式 =====
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
             width: 10px !important;
         }
         .st-option-menu {
             background-color: #f0f2f6;
         }
        /* 一级菜单项 */
        .primary-menu-item {
            padding: 12px 15px;
            margin: 2px 0;
            border-radius: 4px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
        }
        .primary-menu-item:hover {
            background-color: #f0f2f6;
        }
        .primary-menu-item.active {
            background-color: #e6f7ff;
            color: #1890ff;
            border-left: 3px solid #1890ff;
        }

        /* 二级菜单容器 */
        .submenu-container {
            padding-left: 28px;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* 二级菜单项 */
        .submenu-item {
            padding: 8px 15px 8px 25px;
            margin: 1px 0;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }
        .submenu-item:hover {
            background-color: #f5f5f5;
        }
        .submenu-item.active {
            color: #1890ff;
            font-weight: 500;
        }

        /* 图标间距 */
        .menu-icon {
            margin-right: 8px;
            font-size: 16px;
        }
    </style>
    """, unsafe_allow_html=True)
    # 默认样式
    default_styles = {
        "primary": {
            "container": {
                "padding": "0!important",
                "background-color": "#1E293B",  # 深蓝底色
                "border-radius": "8px"
            },
            "icon": {"color": "#94A3B8", "font-size": "14px"},
            "nav-link": {
                "color": "#E2E8F0",
                "font-size": "14px",
                "font-weight": "normal",
                "padding": "10px 15px",
                "margin": "0px",
                "--hover-color": "#334155",
                "border-left": "3px solid transparent"
            },
            "nav-link-selected": {
                "background-color": "#0F172A",
                "color": "#38BDF8",  # 选中项亮蓝色
                "border-left": "3px solid #38BDF8",
                "font-weight": "bold"
            }
        },
        "secondary": {
            "container": {
                "padding": "5px 0 5px 25px!important",  # 左侧缩进
                "background-color": "#1E293B",
                "border-left": "1px dashed #475569"  # 虚线分隔线
            },
            "nav-link": {
                "color": "#94A3B8",
                "font-size": "13px",
                "padding": "5px 15px",
                "margin": "2px 0"
            },
            "nav-link-selected": {
                "background-color": "#334155",
                "color": "#7DD3FC",  # 子菜单选中色
                "font-weight": "normal"
            }
        }
    }
    styles = styles or default_styles

    # 初始化菜单状态
    if f"{key}_primary" not in st.session_state:
        st.session_state[f"{key}_primary"] = primary_options[0]
    if f"{key}_secondary" not in st.session_state:
        st.session_state[f"{key}_secondary"] = None

    with st.sidebar:
        # 一级菜单
        selected_primary = option_menu(
            menu_title=menu_title,
            options=primary_options,
            icons=primary_icons,
            menu_icon="cast",
            default_index=primary_options.index(st.session_state[f"{key}_primary"]),
            styles=styles["primary"],
            key=f"{key}_primary_menu"
        )
        st.session_state[f"{key}_primary"] = selected_primary

        # 二级菜单逻辑
        selected_secondary = None
        submenu_options = submenu_dict.get(selected_primary, [])  # 安全获取子菜单

        if submenu_options:  # 仅当存在子菜单时
            st.markdown(
                f'<div style="margin-top: -10px; margin-bottom: 5px;"></div>',
                unsafe_allow_html=True
            )
            submenu_icon_list = (
                (["circle"] * len(submenu_options))
                if (submenu_icons is None or
                    selected_primary not in submenu_icons or
                    len(submenu_icons[selected_primary]) != len(submenu_options))
                else submenu_icons[selected_primary]
            )

            selected_secondary = option_menu(
                menu_title=None,
                options=submenu_options,
                icons=submenu_icon_list,
                default_index=0,
                styles=styles["secondary"],
                key=f"{key}_secondary_menu_{selected_primary}"
            )
            st.session_state[f"{key}_secondary"] = selected_secondary
    return selected_primary, selected_secondary

