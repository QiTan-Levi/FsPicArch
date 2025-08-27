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
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    personal_watermark: Optional[str] = None
    approved_images_count: int = 0
    likes_received_count: int = 0
    featured_count: int = 0
    account_level: int = 1
    medals_count: int = 0
    registration_time: datetime


    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInfoSelf(UserInfo):
    email: str  # 用户自己可以查看自己的邮箱
    approved_images_count: int = 0
    likes_received_count: int = 0
    uploads_count: int = 0
    views_count: int = 0
    featured_count: int = 0
    analysis_score: Optional[float] = None
    account_level: int = 1
    medals_count: int = 0
    registration_time: datetime
    last_login: Optional[datetime] = None
    queue_limit: int = 5
    max_image_size: Optional[int] = None
    max_image_pixels: Optional[int] = None
    status: int = 5
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 添加 format_dict 函数
def format_dict(data: any, title: str) -> str:
    """
    格式化字典或任何数据为HTML字符串
"""
    if isinstance(data, dict):
        # 处理字典类型
        items = []
        for key, value in data.items():
            # 递归处理嵌套字典
            if isinstance(value, dict):
                nested_html = format_dict(value, str(key))
                items.append(f"""
                <div class="data-row">
                    <div class="data-label">{key}:</div>
                    <div class="data-value">
                        {nested_html}
                    </div>
                </div>
                """)
            else:
                # 处理非字典值
                formatted_value = str(value)
                if len(formatted_value) > 100:
                    formatted_value = formatted_value[:100] + "..."
                items.append(f"""
                <div class="data-row">
                    <div class="data-label">{key}:</div>
                    <div class="data-value">{formatted_value}</div>
                </div>
                """)
        
        return f"""
        <div class="data-section">
            <h4>{title}</h4>
            <div class="data-card">
                {"".join(items)}
            </div>
        </div>
        """
    
    elif isinstance(data, list):
        # 处理列表类型
        items = []
        for i, item in enumerate(data):
            item_html = format_dict(item, f"Item {i}")
            items.append(item_html)
        return f"""
        <div class="data-section">
            <h4>{title}</h4>
            <div class="data-card">
                {"".join(items)}
            </div>
        </div>
        """
    
    else:
        # 处理其他类型（字符串、数字等）
        formatted_value = str(data)
        if len(formatted_value) > 150:
            formatted_value = formatted_value[:150] + "..."
        return f"""
        <div class="data-section">
            <h4>{title}</h4>
            <div class="data-card">
                <div class="data-row">
                    <div class="data-value">{formatted_value}</div>
                </div>
            </div>
        </div>
        """