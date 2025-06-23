# -*- coding: utf-8 -*-
import multiprocessing
import os
import subprocess
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi.openapi.docs import get_swagger_ui_html

#import 顺序注册
# import core.inialize.after_init

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from starlette.staticfiles import StaticFiles

from internal.router.data import data_router
from internal.router.factor import factor_router
from internal.router.misc import misc_router
from internal.router.trading import trading_router
from internal.router.work import work_router
from internal.tasks.fastapi_add_scheduler_runner import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler (no await needed)
    scheduler.start()
    yield
    # Shutdown scheduler (no await needed)
    scheduler.shutdown()
app = FastAPI(
    title="My API",
    version="1.0.0",
    openapi_version="3.0.2",  # 明确指定 OpenAPI 版本
    docs_url=None,default_response_class=ORJSONResponse)

# 挂载静态文件（必须放在路由前面）
app.mount("/static", StaticFiles(directory="static"), name="static")
# Assign lifespan after mounting
app.router.lifespan_context = lifespan

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 覆盖默认的 /docs 路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Docs",
        swagger_js_url="/static/swagger-ui-bundle.min.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png",
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(data_router)
app.include_router(factor_router)
app.include_router(work_router)
app.include_router(trading_router)
app.include_router(misc_router)

add_pagination(app)


def run_streamlit():
    os.system("streamlit run main.py --server.port=8502")

def main():
    # 启动 Streamlit 进程
    p = multiprocessing.Process(target=run_streamlit)
    p.start()
    log_config = "config/log_conf.yaml"
    uvicorn.run("web_server:app", host="0.0.0.0", reload=True, port=8090, log_config=log_config)
    # 确保进程在退出时被终止
    p.join()


if __name__ == "__main__":
    main()
