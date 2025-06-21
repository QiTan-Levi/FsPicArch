# User.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from datetime import datetime
import os
from pathlib import Path
from data_model import UserRegister, UserInfo, AvatarUpdate
from config import Config
from utils.Security import hash_password
from service.SQLsvc import DatabaseService
from service.Email import send_email
from router.OAuth2 import get_current_user
from utils.File import FileService
import datetime

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
    # 获取更新前的用户信息
    old_user_info = DatabaseService.execute_query(
        conn,
        """
        SELECT username, email, bio 
        FROM users WHERE id = %s
        """,
        (current_user["id"],)
    )[0]

    # 构建更新语句
    update_fields = []
    update_values = []
    allowed_fields = ["username", "email", "bio"]
    changed_fields = {}

    for field, value in user_update.items():
        if field in allowed_fields:
            # 只记录实际发生变化的字段
            if str(old_user_info[field]) != str(value):
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                changed_fields[field] = (old_user_info[field], value)
    
    # 检查是否尝试更新不允许的字段
    if not update_fields:
        error_fields = [f"{field} 字段不允许更新" 
                       for field in user_update 
                       if field not in allowed_fields]
        
        if error_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"更新失败: {', '.join(error_fields)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供可更新的字段或新值与旧值相同"
            )
    
    # 特殊字段检查
    if "avatar" in user_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="头像只能通过专门的/me/avatar端点更新"
        )
    if "password" in user_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="密码只能通过专门的/me/password端点更新"
        )
    
    # 执行更新
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
    )[0]

    # 准备邮件模板变量（只包含实际变更的字段）
    template_vars = {
        "USER_NAME": updated_user["username"],
        "NOTIFICATION_TYPE": "Account Changes",
        "UPDATED_FIELDS": "\n".join([
            f'<div class="data-row">'
            f'<div class="data-label">{field}:</div>'
            f'<div class="data-value">'
            f'<span style="text-decoration: line-through; color: #a0aec0;">{old_value}</span> → '
            f'<span class="highlight">{new_value}</span>'
            f'</div>'
            f'</div>'
            for field, (old_value, new_value) in changed_fields.items()
        ]),
        "UPDATE_TIMESTAMP": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "SECURITY_MESSAGE": "If you did not make these changes, please contact adminstrator immediately.",
        "CURRENT_YEAR": datetime.datetime.now().year,
        "COMPANY_NAME": "Byinfo Group"
    }
    # 发送邮件通知（仅当有实际变更时）
    if changed_fields:
        send_email(
            to_email=updated_user["email"],
            subject="用户信息更新通知",
            content=("info_upd", template_vars)  # 使用模板发送
        )

    return updated_user

@router.put("/me/avatar", 
         response_model=UserInfo,
         summary="上传用户头像",
         description="通过二进制流上传用户头像图片")
async def update_user_avatar(
    avatar: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    conn = Depends(DatabaseService.get_db_connection)
):
    # 获取旧头像路径
    old_avatar = DatabaseService.execute_query(
        conn,
        "SELECT avatar FROM users WHERE id = %s",
        (current_user["id"],)
    )
    old_files = [old_avatar[0]["avatar"]] if old_avatar and old_avatar[0]["avatar"] else None
    
    # 使用FileService处理文件上传
    try:
        file_path = await FileService.handle_file_upload(
            file=avatar,
            file_type="avatar",
            upload_dir=AVATAR_DIR,
            old_files=old_files,
            fixed_filename=str(current_user["id"])  # 使用用户ID作为固定文件名
        )
    except HTTPException as e:
        raise e
    
    # 更新数据库中的头像路径
    avatar_url = f"/{file_path}"
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