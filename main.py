import streamlit as st

from internal.pkg.frames import page_config

import asyncio
import nest_asyncio
#import 顺序注册
from web.menu import set_menu

nest_asyncio.apply()
asyncio.set_event_loop(asyncio.new_event_loop())

def main():
    #必须先加载这个
    page_config()
    # 禁用有问题的缓存机制
    st.session_state.disable_static_file_hash = True  # ← 关键修复
    #侧边栏
    set_menu()


#strategy_dict = load_strategy("./config/strategy.yaml")

if __name__ == "__main__":
    main()
