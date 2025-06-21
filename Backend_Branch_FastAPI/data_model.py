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
    avatar: Optional[str] = None
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
    approved_images_count: int = 0
    likes_received_count: int = 0
    uploads_count: int = 0
    account_level: int = 1
    registration_time: datetime
    last_login: Optional[datetime] = None
    bio: Optional[str] = None
    personal_watermark: Optional[str] = None
    medals_count: int = 0
    permission_group: Optional[str] = None
    status: int = 1
    queue_limit: int = 5
    image_view_level_limit: Optional[dict] = None
    featured_count: int = 0
    views_count: int = 0
    unique_identifier: Optional[str] = None 
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }