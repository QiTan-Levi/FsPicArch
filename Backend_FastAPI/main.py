# main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# 初始化 FastAPI 应用
app = FastAPI(
    title="FsPicArch 图片存档系统 API",  # 应用标题
    description="航空和铁路图片存档系统的用户认证接口",  # 应用描述
    version="0.0.1dev",  # 应用版本号
    docs_url=None,  # 禁用默认的/docs文档路由
    redoc_url=None,  # 禁用默认的/redoc文档路由
    swagger_ui_init_oauth={  # 设置 Swagger UI 的 OAuth2 配置
        "clientId": "your-client-id",  # OAuth2客户端ID
        "scopes": {  # 定义可用权限范围
            "read:users": "读取用户信息",
            "write:users": "修改用户信息"
        },
        "usePkceWithAuthorizationCodeGrant": True  # 启用PKCE增强安全性
    }
)

# 导入并注册路由模块
from router.OAuth2 import router as oauth2_router  # OAuth2认证路由
app.include_router(oauth2_router)  # 将OAuth2路由添加到应用

from router.User import router as user_router  # 用户管理路由
app.include_router(user_router)  # 将用户路由添加到应用

from router.Static import router as static_router  # 静态文件路由
app.include_router(static_router)  # 将静态文件路由添加到应用

# OpenAPI 配置函数
def custom_openapi():
    # 如果已经生成过schema则直接返回
    if app.openapi_schema:
        return app.openapi_schema
    
    # 获取基础OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加安全配置
    openapi_schema["components"] = {
        "securitySchemes": {
            "OAuth2PasswordBearer": {  # 定义OAuth2密码模式
                "type": "oauth2",
                "flows": {
                    "password": {  # 密码授权流程
                        "tokenUrl": "oauth2/token",  # 令牌获取URL
                        "scopes": {  # 权限范围定义
                            "read:users": "读取用户信息",
                            "write:users": "修改用户信息"
                        }
                    }
                }
            }
        }
    }
    
    # 缓存schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 自定义Swagger UI路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",  # OpenAPI schema文件路径
        title="FsPicArch API 文档",  # 文档标题
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",  # 文档图标
        oauth2_redirect_url="/docs/oauth2-redirect",  # OAuth2重定向URL
        init_oauth={  # 初始化OAuth2配置
            "clientId": "your-client-id",  # 客户端ID
            "scopes": ["read:users", "write:users"]  # 请求的权限范围
        }
    )

# 主程序入口
if __name__ == "__main__":
    import uvicorn
    # 使用uvicorn运行FastAPI应用
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 监听所有网络接口的8000端口