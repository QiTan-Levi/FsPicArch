# User.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from datetime import datetime
import os
from pathlib import Path
from data_model import UserRegister, UserInfo, AvatarUpdate
from config import Config
from utils.Security import hash_password
from service.SQLsvc import DatabaseService
from router.OAuth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["用户信息"]
)

# 确保头像存储目录存在
AVATAR_DIR = "static/avatar"
Path(AVATAR_DIR).mkdir(parents=True, exist_ok=True)

@router.post("/register", 
          response_model=UserInfo,
          summary="用户注册",
          description="注册一个新用户账号")
async def register(user: UserRegister, conn = Depends(DatabaseService.get_db_connection)):
    # 检查用户名和邮箱是否已存在
    if DatabaseService.get_user_by_username(conn, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )
    
    if DatabaseService.execute_query(conn, "SELECT id FROM users WHERE email = %s", (user.email,)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    # 创建用户
    user_data = {
        'username': user.username,
        'password': hash_password(user.password),
        'email': user.email,
        'avatar': user.avatar,
        'bio': user.bio
    }
    new_user = DatabaseService.create_user(conn, user_data)
    return new_user[0]

@router.get("/me/deactivated",
         summary="用户注销",
         description="注销当前登录用户")
async def deactivate_user(
    current_user: dict = Depends(get_current_user),
    conn = Depends(DatabaseService.get_db_connection)
):
    DatabaseService.execute_update(
        conn,
        "UPDATE users SET status = 4 WHERE id = %s",
        (current_user["id"],)
    )
    return {"message": "用户已注销"}

@router.get("/me", 
         response_model=UserInfo,
         summary="获取当前用户信息",
         description="获取当前登录用户的详细信息")
async def read_users_me(
    current_user: dict = Depends(get_current_user), 
    conn = Depends(DatabaseService.get_db_connection)
):
    users = DatabaseService.execute_query(
        conn,
        """
        SELECT 
            id, username, email, avatar, approved_images_count, 
            likes_received_count, uploads_count, account_level, registration_time,
            last_login, bio, personal_watermark, account_level, medals_count,
            permission_group, status, queue_limit, image_view_level_limit,
            featured_count, views_count, unique_identifier
        FROM users 
        WHERE id = %s
        """,
        (current_user["id"],)
    )
    
    user_data = users[0]
    # 确保返回的数据不包含排除的字段
    excluded_fields = ['analysis_score', 'notes', 'inviter_id']
    for field in excluded_fields:
        if field in user_data:
            del user_data[field]
    
    return user_data

@router.put("/update", 
         response_model=UserInfo,
         summary="更新用户信息",
         description="更新当前登录用户的个人信息")
async def update_user_info(
    user_update: dict,
    current_user: dict = Depends(get_current_user),
    conn = Depends(DatabaseService.get_db_connection)
):
    # 检查是否尝试更新 avatar 字段
    if "avatar" in user_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="头像只能通过专门的/me/avatar端点更新"
        )
    
    # 构建更新语句
    update_fields = []
    update_values = []
    for field, value in user_update.items():
        if field in ["username", "email", "bio"]:  # 移除了 avatar
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供有效的更新字段"
        )
    
    update_values.append(current_user["id"])
    
    DatabaseService.execute_update(
        conn,
        f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s",
        update_values
    )
    
    # 获取更新后的用户信息
    updated_user = DatabaseService.execute_query(
        conn,
        """
        SELECT id, username, email, avatar, approved_images_count, 
               likes_received_count, uploads_count, account_level, registration_time
        FROM users WHERE id = %s
        """,
        (current_user["id"],)
    )
    
    return updated_user[0]

@router.put("/me/avatar", 
         response_model=UserInfo,
         summary="上传用户头像",
         description="通过二进制流上传用户头像图片")
async def update_user_avatar(
    avatar: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    conn = Depends(DatabaseService.get_db_connection)
):
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png"]
    if avatar.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持JPEG、PNG的图片"
        )
    
    # 验证文件大小（例如限制为2MB）
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    contents = await avatar.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="头像文件大小不能超过2MB"
        )
    
    # 验证文件扩展名
    file_ext = avatar.filename.split('.')[-1].lower()
    if file_ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件扩展名"
        )
    
    # 验证确实是图片文件（简单验证）
    try:
        from PIL import Image
        import io
        Image.open(io.BytesIO(contents)).verify()
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件"
        )
    
    # 生成唯一文件名
    filename = f"{current_user['id']}.{file_ext}"  # 固定文件名，覆盖旧文件
    file_path = os.path.join(AVATAR_DIR, filename)
    
    # 删除旧头像文件（如果存在）
    old_avatar = DatabaseService.execute_query(
        conn,
        "SELECT avatar FROM users WHERE id = %s",
        (current_user["id"],)
    )
    if old_avatar and old_avatar[0]["avatar"]:
        old_path = old_avatar[0]["avatar"].lstrip('/')
        try:
            if os.path.exists(old_path):
                os.remove(old_path)
        except:
            pass  # 如果删除旧文件失败，继续处理新文件
    
    # 保存新文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存头像文件时出错: {str(e)}"
        )
    
    # 更新数据库中的头像路径
    avatar_url = f"/{AVATAR_DIR}/{filename}"
    DatabaseService.execute_update(
        conn,
        "UPDATE users SET avatar = %s WHERE id = %s",
        (avatar_url, current_user["id"])
    )
    
    # 获取更新后的用户信息
    updated_user = DatabaseService.execute_query(
        conn,
        """
        SELECT id, username, email, avatar, approved_images_count, 
               likes_received_count, uploads_count, account_level, registration_time
        FROM users WHERE id = %s
        """,
        (current_user["id"],)
    )
    
    return updated_user[0]