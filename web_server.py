# -*- coding: utf-8 -*-
import uvicorn
from fastapi.openapi.docs import get_swagger_ui_html

#import 顺序注册
import core.inialize.pre_init
# import core.inialize.after_init

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from core.rest.data import data_router
from core.rest.factor import factor_router
from core.rest.misc import misc_router
from core.rest.trading import trading_router
from core.rest.work import work_router


app = FastAPI(title="My API",
    version="1.0.0",
    openapi_version="3.0.2",  # 明确指定 OpenAPI 版本
    docs_url="/docs",default_response_class=ORJSONResponse)

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
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
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

def main():
    log_config = "config/log_conf.yaml"
    uvicorn.run("web_server:app", host="0.0.0.0", reload=True, port=8090, log_config=log_config)


if __name__ == "__main__":
    main()
