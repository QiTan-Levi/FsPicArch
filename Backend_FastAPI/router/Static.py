from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
from config import Config

router = APIRouter(
    tags=["静态服务"],  # 这将使该路由在API文档中被分类为"静态服务"
    responses={404: {"description": "未找到"}}
)

# 基础静态文件目录
STATIC_BASE_DIR = Config.STATIC_FILES_DIR

@router.get("/statics/{folder}/{filename}",
           summary="获取静态文件",
           description="获取大部分用户产生的静态文件，如头像、程序文件等",
           response_description="请求的文件内容")
async def get_static_file(folder: str, filename: str):
    """
    获取静态文件
    
    - **folder**: 静态文件所在的文件夹名 (如 avatar, prog 等)
    - **filename**: 请求的文件名
    """
    # 构造文件路径
    file_path = Path(STATIC_BASE_DIR) / folder / filename
    
    # 安全检查：防止目录遍历攻击
    try:
        file_path.resolve().relative_to(Path(STATIC_BASE_DIR).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="禁止访问")
    
    from service.Email import send_email

    # 检查文件是否存在
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件未找到")
    
    # 返回文件
    return FileResponse(file_path)