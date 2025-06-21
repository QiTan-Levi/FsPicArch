# data_model.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import UploadFile

class AvatarUpdate(BaseModel):
    avatar: UploadFile

class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    bio: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class OAuthClient(BaseModel):  # 新增客户端模型
    client_id: str
    client_secret: str
    redirect_uris: list[str]  # 允许的回调 URL
    scope: str | None = None

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    personal_watermark: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }