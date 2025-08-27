# OAuth2.py
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt as pyjwt
from pydantic import BaseModel
from src.data_model import TokenData, Token
from src.config import Config
from service.SQLsvc import execute_sql

router = APIRouter(
    prefix="/oauth2",
    tags=["认证授权"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth2/token")

def password_security(password: str, hashed: str = None) -> str | bool:
    """2合1密码安全函数：
    - 仅传password时返回哈希值
    - 传password和hashed时返回校验结果
    """
    hashed_val = hashlib.sha256(password.encode()).hexdigest()
    if hashed is None:
        return hashed_val
    return hashed_val == hashed

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
    
    users = execute_sql(
        auto={
            "op": "read",
            "table": "users",
            "where": {"username": token_data.username}
        }
    )
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
):
    # 1. 检查用户是否存在
    users = execute_sql(
        auto={
            "op": "read",
            "table": "users",
            "where": {"username": form_data.username}
        }
    )
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = users[0]
    
    # 2. 检查密码是否正确
    if not password_security(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 更新最后登录时间
    execute_sql(
        query="UPDATE users SET last_login = NOW() WHERE id = %s",
        params=(user["id"],)
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