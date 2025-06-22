from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
import hashlib
from typing import Optional


def testPage():
    # Add Title
    st.title("🚲 Bike Sharing Data Analysis with Pygwalker")

    # Initialize renderer with error handling
    try:
        renderer = get_pyg_renderer()
    except Exception as e:
        st.error(f"Failed to initialize Pygwalker: {str(e)}")
        st.stop()

    st.subheader("Interactive Data Explorer")

    # Create tabs (remove key parameter)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Explorer", "🔍 Data Profiling", "📈 Chart Viewer", "🖼️ Saved Charts", "🗃️ Raw Data"]
    )

    with tab1:
        st.markdown("### Full Interactive UI")
        renderer.explorer(key=generate_key("explorer_full"))

    with tab2:
        st.markdown("### Data Analysis")
        renderer.explorer(
            default_tab="data",
            key=generate_key("explorer_data")
        )

    with tab3:
        st.markdown("### Visualization Gallery")
        renderer.viewer(key=generate_key("viewer"))

    with tab4:
        st.markdown("### Pre-saved Charts")
        render_saved_charts(renderer)

    with tab5:
        st.markdown("### Raw Dataset Preview")
        renderer.table(key=generate_key("table"))


def generate_key(prefix: str) -> str:
    """Generate unique key for Streamlit elements"""
    return f"{prefix}_{hashlib.md5(prefix.encode()).hexdigest()[:8]}"


def render_saved_charts(renderer: StreamlitRenderer, max_charts: int = 2):
    """直接渲染预定义的图表（修复版）"""
    try:
        st.markdown("### Registered Rides by Weekday")
        # 第一个图表（确保至少有一个图表）
        renderer.chart(0)

        st.markdown("### Registered Rides by Day")
        # 第二个图表（确保至少有两个图表）
        if len(renderer.walker.vis_spec) > 1:
            renderer.chart(1)
        else:
            st.warning("请先在探索界面创建至少两个图表")

    except IndexError:
        st.error("图表未找到，请先在探索界面创建图表")
        if st.button("前往探索界面", key="go_to_explorer"):
            st.session_state.active_tab = "📊 Explorer"
    except Exception as e:
        st.error(f"渲染图表失败: {str(e)}")
    # """Safely render saved charts with error handling"""
    # try:
    #     # Check if charts exist
    #     if not hasattr(renderer.walker, 'vis_spec') or len(renderer.walker.vis_spec) == 0:
    #         st.warning("No saved charts found. Please create charts in the Explorer tab first.")
    #         if st.button("Go to Explorer", key=generate_key("go_to_explorer")):
    #             st.switch_page("?tab=explorer")
    #         return
    #
    #     # Render available charts
    #     for i in range(min(len(renderer.walker.vis_spec), max_charts)):
    #         try:
    #             col1, col2 = st.columns(2)
    #             with col1:
    #                 if i == 0:
    #                     st.markdown("#### Registered Rides by Weekday")
    #                 elif i == 1:
    #                     st.markdown("#### Registered Rides by Hour")
    #             with col2:
    #                 renderer.chart(
    #                     i,
    #                     key=generate_key(f"chart_{i}")
    #                 )
    #         except Exception as e:
    #             st.error(f"Error rendering chart {i}: {str(e)}")
    #
    # except Exception as e:
    #     st.error(f"Chart rendering failed: {str(e)}")


@st.cache_resource
def get_pyg_renderer() -> StreamlitRenderer:
    """Initialize Pygwalker renderer with caching"""
    try:
        df = pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")

        # Data preprocessing example
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['weekday'] = df['date'].dt.day_name()
            df['hour'] = df['date'].dt.hour

        return StreamlitRenderer(
            df,
            spec="./gw_config.json",
            spec_io_mode="rw",  # Enable read/write for saving charts
            kernel_computation=True,  # For better performance
            # Add unique key for the renderer
            key=generate_key("pygwalker_renderer")
        )
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        raise