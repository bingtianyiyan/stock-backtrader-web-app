# ---------------------- 使用示例 ----------------------
from core.pkg.logger.config import FileWriterArgs, LoggerConfig, WriteTo
from core.pkg.logger.logger import  new_log


if __name__ == "__main__":
#def test_log():
    # 获取当前文件所在目录的父级父级目录（即项目根目录）
    # BASE_DIR = Path(__file__).parent.parent.parent  # 根据实际层级调整
    # LOG_DIR = BASE_DIR / "logs"  # 项目根目录下的logs文件夹
    # LOG_DIR.mkdir(exist_ok=True)  # 自动创建目录
    # 初始化日志（输出到控制台和文件）
    # 自定义配置
    config = LoggerConfig(
        driver="loguru",
        level="debug",
        write_to=[
            WriteTo(name="file", args=FileWriterArgs(path="logs/app_{time:YYYY-MM-DD}.log")),
            WriteTo(name="console", args=None)
        ]
    )

    # 初始化日志
    logger = new_log(config)

    # 上下文绑定
    logger.info("This is a test message", user_id=123, action="login")
    logger.bind(request_id="abc123").warn("Bound message", details={"page": "home"})
