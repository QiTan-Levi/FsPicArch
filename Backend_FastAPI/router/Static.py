from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from service.File import file_service_execute
import jwt as pyjwt
from fastapi.security import OAuth2PasswordBearer
from src.config import Config
from service.SQLsvc import execute_sql

router = APIRouter(prefix="/static", tags=["文件服务"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2/token")

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    验证OAuth2令牌并返回user_id
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证令牌")
    try:
        payload = pyjwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
        # 查询用户id
        result = execute_sql(auto={
            "op": "read",
            "table": "users",
            "where": {"username": username}
        })
        if not result or not isinstance(result, list):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        user_id = str(result[0]["id"])
        return user_id
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌校验失败")

@router.get("")
async def file_crud(
    op: str,
    file: Optional[UploadFile] = None,
    file_info: Dict[str, Any] = {},
    old_files: Optional[List[str]] = None,
    fixed_filename: Optional[str] = None,
    user_id: str = Depends(verify_token)
):
    """
    文件服务统一API，支持CRUD
    需通过OAuth2 Bearer认证
    """
    result = await file_service_execute(op, user_id, file, file_info, old_files, fixed_filename)
    if 'error' in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

def _get_mime_type(filename: str) -> str:
    """根据文件名返回对应的MIME类型"""
    ext = os.path.splitext(filename)[1].lower()
    return {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.zip': 'application/zip',
    }.get(ext, 'application/octet-stream')

@router.get("/public/{related_table}/{ident_hash}/{related_id}")
async def get_public_file(
    related_table: str,
    ident_hash: str,
    related_id: int
):
    """
    公共文件访问接口
    只有当files表中is_public=TRUE时才返回文件
    """
    # 查询文件记录
    result = execute_sql(auto={
        "op": "read",
        "table": "files",
        "where": {
            "related_table": related_table,
            "related_id": related_id,
            "file_tag": ident_hash,
            "is_public": True,  # 必须为公开文件
            "status": 1  # 且状态正常
        }
    })
    
    # 检查查询结果
    if not result or not isinstance(result, list):
        raise HTTPException(
            status_code=404,
            detail="文件不存在或未公开"
        )
    
    file_record = result[0]
    file_path = file_record["file_path"]
    
    # 检查物理文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="文件存储异常，请联系管理员"
        )
    
    # 流式返回文件
    def iterfile():
        with open(file_path, "rb") as f:
            yield from f
            
    return StreamingResponse(
        iterfile(),
        media_type=_get_mime_type(file_record["file_name"]),
        headers={
            "Content-Disposition": f"inline; filename={file_record['file_name']}",
            "Cache-Control": "public, max-age=3600"  # 缓存1小时
        }
    )

