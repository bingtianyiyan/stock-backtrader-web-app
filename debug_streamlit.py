import subprocess
import sys
import asyncio
import nest_asyncio
from streamlit.web.cli import main as st_main

#调试streamlit 启动这个

def is_streamlit_running():
    """检查是否已有Streamlit进程运行"""
    try:
        from streamlit.runtime.runtime import Runtime
        return Runtime.instance() is not None
    except:
        return False


def fix_async():
    """修复异步事件循环冲突"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    nest_asyncio.apply()
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())


def run_as_subprocess():
    """使用子进程方式运行Streamlit"""
    try:
        subprocess.run([
            sys.executable,
            "-m", "streamlit",
            "run", "main.py",  # 改为你的主入口文件
            "--server.port=8502",
            "--server.headless=true"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit启动失败: {e}")
        sys.exit(1)


def main():
    fix_async()

    if not is_streamlit_running():
        # 方案1：直接调用（适合调试）
        sys.argv = ["streamlit", "run", "main.py","--server.port=8502"]  # 明确指定主文件
        sys.exit(st_main())

        # 或者方案2：使用子进程（更稳定）
        # run_as_subprocess()


if __name__ == "__main__":
    main()