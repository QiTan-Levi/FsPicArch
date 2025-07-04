# OAuth2.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt as pyjwt
from pydantic import BaseModel
from data_model import TokenData, Token
from config import Config
from utils.Security import verify_password
from service.SQLsvc import DatabaseService

router = APIRouter(
    prefix="/oauth2",
    tags=["认证授权"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth2/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    conn = Depends(DatabaseService.get_db_connection)
):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = pyjwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except pyjwt.PyJWTError:
        raise credentials_exception
    
    users = DatabaseService.get_user_by_username(conn, token_data.username)
    if not users:
        raise credentials_exception
    return users[0]

@router.post("/token", 
          response_model=Token,
          summary="获取访问令牌",
          description="使用用户名和密码获取访问令牌")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn = Depends(DatabaseService.get_db_connection)
):
    # 1. 检查用户是否存在
    users = DatabaseService.get_user_by_username(conn, form_data.username)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = users[0]
    
    # 2. 检查密码是否正确
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 更新最后登录时间
    DatabaseService.execute_update(
        conn,
        "UPDATE users SET last_login = NOW() WHERE id = %s",
        (user["id"],)
    )
    
    # 4. 生成访问令牌
    access_token_expires = timedelta(minutes=Config.TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    # 5. 设置 HttpOnly 的 cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=Config.TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", 
          summary="用户登出",
          description="清除用户的认证令牌")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "成功登出"}