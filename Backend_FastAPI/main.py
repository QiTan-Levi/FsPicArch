# main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# 初始化 FastAPI 应用
app = FastAPI(
    title="FsPicArch 图片存档系统 API",
    description="航空和铁路图片存档系统的用户认证接口",
    version="0.0.1dev",
    docs_url=None,
    redoc_url=None,
    swagger_ui_init_oauth={
        "clientId": "your-client-id", 
        "scopes": {
            "read:users": "读取用户信息",
            "write:users": "修改用户信息"
        },
        "usePkceWithAuthorizationCodeGrant": True
    }
)

# 导入路由
from router.OAuth2 import router as oauth2_router
app.include_router(oauth2_router)

from router.User import router as user_router
app.include_router(user_router)

from router.Static import router as static_router
app.include_router(static_router)

# OpenAPI 配置
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"] = {
        "securitySchemes": {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "oauth2/token",
                        "scopes": {
                            "read:users": "读取用户信息",
                            "write:users": "修改用户信息"
                        }
                    }
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FsPicArch API 文档",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        oauth2_redirect_url="/docs/oauth2-redirect",
        init_oauth={
            "clientId": "your-client-id",
            "scopes": ["read:users", "write:users"]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)