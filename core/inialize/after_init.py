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


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(data_router)
app.include_router(factor_router)
app.include_router(work_router)
app.include_router(trading_router)
app.include_router(misc_router)

add_pagination(app)

# def after_init():
#     print("after_init called")
