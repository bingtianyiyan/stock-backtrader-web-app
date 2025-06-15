import atexit
import sys
from typing import List, Callable

_exit_handlers: List[Callable] = []

def register_exit_handler(handler: Callable, prepend=False):
    """注册退出钩子"""
    if prepend:
        _exit_handlers.insert(0, handler)
    else:
        _exit_handlers.append(handler)
    atexit.register(_run_handlers)

def _run_handlers():
    """执行所有退出处理器"""
    for handler in _exit_handlers:
        try:
            handler()
        except Exception as e:
            print(f"Exit handler error: {e}", file=sys.stderr)

def exit(code=0):
    """带处理器退出的系统调用"""
    _run_handlers()
    sys.exit(code)