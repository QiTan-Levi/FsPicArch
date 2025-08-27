# User.py
import hashlib
import json
import zlib
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
import user_agents  # 需要安装 pip install pyyaml ua-parser user-agents
from datetime import datetime
import os
from pathlib import Path
from src.data_model import UserRegister, UserInfo, AvatarUpdate, UserInfoSelf, format_dict
from src.config import Config
from service.SQLsvc import execute_sql
from service.Email import send_email
from router.OAuth2 import get_current_user
from service.File import file_service_execute
import datetime

router = APIRouter(
    prefix="/users",
    tags=["用户信息"]
)

def password_security(password: str, hashed: str = None) -> str | bool:
    """2合1密码安全函数：
    - 仅传password时返回哈希值
    - 传password和hashed时返回校验结果
    """
    hashed_val = hashlib.sha256(password.encode()).hexdigest()
    if hashed is None:
        return hashed_val
    return hashed_val == hashed

# 确保头像存储目录存在
AVATAR_DIR = "static/avatar"
Path(AVATAR_DIR).mkdir(parents=True, exist_ok=True)
@router.post("/register", 
          response_model=UserInfo,
          summary="用户注册",
          description="注册一个新用户账号")
async def register(user: UserRegister):
    try:
        # 检查用户名和邮箱是否已存在
        existing_username = execute_sql(
            query="SELECT id FROM users WHERE username = %s",
            params=(user.username,)
        )
        
        if existing_username and isinstance(existing_username, list) and len(existing_username) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        
        existing_email = execute_sql(
            query="SELECT id FROM users WHERE email = %s",
            params=(user.email,)
        )
        if existing_email and isinstance(existing_email, list) and len(existing_email) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        
        # 准备用户数据
        checkidd = str(format(zlib.crc32(hashlib.sha256((user.username + user.email + user.password).encode('utf-8')).hexdigest().encode('utf-8')) & 0xFFFFFF, '06x'))
        hashed_password = password_security(user.password)
        
        # 修改为MySQL兼容的插入语法
        execute_sql(
            query="""
            INSERT INTO users 
            (username, password, email, bio, notes, status, registration_time) 
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            params=(
                user.username,
                hashed_password,
                user.email,
                user.bio,
                json.dumps({'verify_tempcode': checkidd}),  # 将字典转为JSON字符串
                5  # 未验证状态
            )
        )
        
        # 获取最后插入的ID
        result = execute_sql(
            query="SELECT LAST_INSERT_ID() AS id",
            params=()
        )
        
        if not result or not isinstance(result, list) or len(result) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无法获取新用户ID"
            )
        
        user_id = result[0]['id']
        
        # 获取完整用户信息
        new_user = execute_sql(
            query="SELECT * FROM users WHERE id = %s",
            params=(user_id,)
        )
        
        if not new_user or not isinstance(new_user, list) or len(new_user) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无法获取新创建的用户信息"
            )
        
        new_user = new_user[0]
        
        # 确保 unique_identifier 存在
        if 'unique_identifier' not in new_user or not new_user['unique_identifier']:
            execute_sql(
                query="UPDATE users SET unique_identifier = UUID() WHERE id = %s",
                params=(user_id,)
            )
            # 重新获取用户数据
            new_user = execute_sql(
                query="SELECT * FROM users WHERE id = %s",
                params=(user_id,)
            )[0]
        
        # 发送成功注册邮件
        if Config.SECONDARY_ENHANCED_EMAIL_VERIFICATION:
            VERIFICATION_LINK = f"{Config.FRONTEND_URL}/verify_email/{new_user['unique_identifier']}"
        else:
            VERIFICATION_LINK = f"{Config.BACKEND_URL}/users/fast_verify_email/{new_user['unique_identifier']}"
        
        # 在注册函数中修改邮件发送部分
        try:
            # 发送成功注册邮件
            if Config.SECONDARY_ENHANCED_EMAIL_VERIFICATION:
                VERIFICATION_LINK = f"{Config.FRONTEND_URL}/verify_email/{new_user['unique_identifier']}"
            else:
                VERIFICATION_LINK = f"{Config.BACKEND_URL}/users/fast_verify_email/{new_user['unique_identifier']}"
            
            email_result = send_email(
                to_email=user.email,
                subject="欢迎注册 FsPicArch",
                content=("welcome", {
                    "USER_NAME": user.username,
                    "VERIFICATION_LINK": VERIFICATION_LINK,
                    "CURRENT_YEAR": datetime.datetime.now().year,
                })
            )
            
            # 检查邮件发送结果
            if isinstance(email_result, tuple) and not email_result[0]:
                print(f"邮件发送失败: {email_result[1]}")
                # 可以记录到日志但不中断注册流程
        except Exception as email_error:
            print(f"邮件发送过程中出错: {str(email_error)}")

        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册过程中出现内部错误: {str(e)}"
        )
    

@router.get("/me/deactivated",
         summary="用户注销",
         description="注销当前登录用户")
async def deactivate_user(
    current_user: dict = Depends(get_current_user)
):
    execute_sql(
        query="UPDATE users SET status = 4 WHERE id = %s",
        params=(current_user["id"],)
    )
    return {"message": "用户已注销"}

@router.get("/me", 
         response_model=UserInfoSelf,
         summary="获取当前用户信息",
         description="获取当前登录用户的详细信息")
async def read_users_me(
    current_user: dict = Depends(get_current_user)
):
    users = execute_sql(
        query="""
        SELECT 
            id, username, email, avatar, approved_images_count, 
            likes_received_count, uploads_count, account_level, registration_time,
            last_login, bio, personal_watermark, account_level, medals_count,
            permission_group, status, queue_limit, image_view_level_limit,
            featured_count, views_count, unique_identifier
        FROM users 
        WHERE id = %s
        """,
        params=(current_user["id"],)
    )
    
    user_data = users[0]
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
    current_user: dict = Depends(get_current_user)
):
    old_user_info = execute_sql(
        query="""
        SELECT username, email, bio 
        FROM users WHERE id = %s
        """,
        params=(current_user["id"],)
    )[0]

    update_fields = []
    update_values = []
    allowed_fields = ["username", "email", "bio"]
    changed_fields = {}

    for field, value in user_update.items():
        if field in allowed_fields:
            if str(old_user_info[field]) != str(value):
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                changed_fields[field] = (old_user_info[field], value)
    
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
    
    update_values.append(current_user["id"])
    execute_sql(
        query=f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s",
        params=update_values
    )
        
    updated_user = execute_sql(
        query="""
        SELECT id, username, email, avatar, approved_images_count, 
            likes_received_count, uploads_count, account_level, registration_time
        FROM users WHERE id = %s
        """,
        params=(current_user["id"],)
    )[0]

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
    if changed_fields:
        send_email(
            to_email=updated_user["email"],
            subject="用户信息更新通知",
            content=("info_upd", template_vars)
        )

    return updated_user

@router.put("/me/avatar", 
         response_model=UserInfo,
         summary="上传用户头像",
         description="通过二进制流上传用户头像图片")
async def update_user_avatar(
    avatar: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    old_avatar = execute_sql(
        query="SELECT avatar FROM users WHERE id = %s",
        params=(current_user["id"],)
    )
    old_files = None
    if old_avatar and old_avatar[0]["avatar"]:
        # 统一用文件系统路径
        old_path = old_avatar[0]["avatar"].replace('/', os.sep).lstrip(os.sep)
        old_files = [old_path]
    
    try:
        # 使用最新的 file_service_execute，自动生成 ident_code
        result = await file_service_execute(
            op="create",
            user_id=current_user["id"],
            file=avatar,
            file_info={
                "file_type": "avatar",
                "upload_dir": AVATAR_DIR,
                "related_id": current_user["id"],
                "related_table": "users"
            },
            old_files=old_files,
            fixed_filename=str(current_user["id"])
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        file_path = result['file_path']
        ident_code = result.get('ident_code')

    except HTTPException as e:
        raise e

    # 统一 URL 路径格式（与实际保存一致）
    # 获取新文件名（与 FileService 生成一致）
    file_ext = avatar.filename.split('.')[-1].lower()
    crc = result.get('ident_code', '').split('_')[-1] if result.get('ident_code') else 'hash'
    hash_part = file_path.split('_')[-1].split('.')[0] if '_' in file_path else 'random'
    avatar_filename = file_path.split(os.sep)[-1] if os.sep in file_path else file_path.split('/')[-1]
    avatar_url = f"/static/avatar/{avatar_filename}"
    # 同步 ident_code 到用户表
    execute_sql(
        query="UPDATE users SET avatar = %s, notes = JSON_SET(COALESCE(notes, '{{}}'), '$.avatar_ident_code', %s) WHERE id = %s",
        params=(avatar_url, ident_code, current_user["id"])
    )

    updated_user = execute_sql(
        query="""
        SELECT id, username, email, avatar, approved_images_count, 
               likes_received_count, uploads_count, account_level, registration_time
        FROM users WHERE id = %s
        """,
        params=(current_user["id"],)
    )

    return updated_user[0]

@router.post("/varify_email/{identify_temp_code}",
            summary="验证用户邮箱",
            description="")
async def varify_email_newuser(
    verify_temp: str,
    identify_temp_code: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    if not Config.SECONDARY_ENHANCED_EMAIL_VERIFICATION:
        try:
            # 获取请求信息
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # 获取请求头
            headers = {k: v for k, v in request.headers.items()}
            
            # 获取请求体
            try:
                body = await request.json()
            except:
                body = "无法解析为JSON"
            
            # 解析User-Agent
            try:
                ua = user_agents.parse(user_agent)
                browser = f"{ua.browser.family} {ua.browser.version_string}"
                device = f"{ua.device.family} {ua.os.family} {ua.os.version_string}"
            except:
                browser = "unknown"
                device = "unknown"
            
            current_user_foralert = {
                'id': current_user['id'],
                'username': current_user['username'],
                'email': f'<a herf="mailto:{current_user['email']}?subject=关于您的账户访问确认&body=您好，我们检测到您的账户({current_user['username']})在{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}尝试了邮箱验证操作。请问这是您本人的操作吗？\n\n设备信息：{device}\n浏览器：{browser}\n\n如果您发现系统存在漏洞欢迎反馈，若是误操作也请告知具体情况。"></a>',
                'status': current_user['status'],
                'account_level': current_user['account_level'],
                'registration_time': current_user['registration_time'],
                'last_login': current_user['last_login'],
                'unique_identifier': current_user['unique_identifier'],
                'avatar': current_user['avatar'],
                'analysis_score': current_user['analysis_score'],
                'permission_group': current_user['permission_group'],
                'bio': current_user['bio'],
                'notes': current_user['notes']
            }
            # 准备模板变量
            template_vars = {
                "NOTIFICATION_HEADER": "SECURITY ALERT - 未授权访问尝试",
                "NOTIFICATION_TYPE": "高优先级安全事件",
                "UPDATE_TIMESTAMP": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "SECURITY_MESSAGE": "用户尝试绕过邮箱验证，请立即审查此活动",
                "CURRENT_YEAR": datetime.datetime.now().year,
                "COMPANY_NAME": "Byinfo Group",
                "USER_DATA": format_dict(current_user_foralert, "用户数据"),
                "REQUEST_HEADERS": format_dict(headers, "请求头"),
                "REQUEST_BODY": format_dict(body, "请求体"),
                "CLIENT_INFO": {
                    "IP Address": client_ip,
                    "Browser": browser,
                    "Device": device,
                    "Endpoint": f"/users/verify_email/{identify_temp_code}",
                    "Temp Code": verify_temp
                }
            }
            
            # 发送邮件
            success, message = send_email(
                to_email=Config.ADMIN_EMAIL,
                subject=f"SECURITY ALERT: {current_user['username']} 尝试绕过邮箱验证",
                content=("wuquanxian_alert", template_vars)
            )
            
            if not success:
                print(f"邮件发送失败: {message}")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前系统未启用SEEV, 安全事件已上报"
            )
            
        except Exception as e:
            print(f"处理安全事件时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="处理安全事件时发生内部错误"
            )
    
    user = execute_sql(
        auto={
            "op": "read",
            "table": "users",
            "where": {"id": current_user["id"]}
        }
    )
    user_uuid = user[0]["unique_identifier"]
    if user[0]["notes"]:
        user_code = user[0]["notes"].get("verify_tempcode")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
    if user[0]["status"] != 5:
        #404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    if user_uuid != identify_temp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证失败，链接无效. byURL",
        )
    
    if user_code != verify_temp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证失败，链接无效. byCODE",
        )
    
    if user_code == verify_temp and user[0]["status"] == 5 and identify_temp_code == user_uuid:
        execute_sql(
            query="UPDATE users SET status = 1, notes = NULL , permission_group = user WHERE id = %s AND unique_identifier = %s",
            params=(current_user["id"], identify_temp_code)
        )
        return {"message": "邮箱验证成功，用户状态已更新为正常."}

@router.get("/fast_verify_email/{identify_temp_code}")
async def fast_verify_email(identify_temp_code: str, request: Request):
    """
    快速验证邮箱地址的端点
    identify_temp_code: 用户临时验证码
    """
    
    # 检查是否启用了增强验证
    if Config.SECONDARY_ENHANCED_EMAIL_VERIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"当前系统启用SEEV，此URL无效，邮件可能错误发送，请联系管理员（{Config.ADMIN_EMAIL}）"
        )
    
    # 使用参数化查询防止SQL注入
    user = execute_sql(
        auto={
            "op": "read",
            "table": "users",
            "where": {"unique_identifier": identify_temp_code}
        }
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="验证链接无效或已过期"
        )
        
    if user[0]["status"] != 5:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="验证链接已使用或已过期"
        )
    
    # 更新用户状态
    update_result = execute_sql(
        query="UPDATE users SET status = 1, notes = NULL, permission_group = %s WHERE id = %s AND unique_identifier = %s",
        params=("default_group", user[0]["id"], identify_temp_code)  # 添加缺失的 permission_group 参数
    )

    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误，请稍后重试"
        )
    
    # 使用上下文管理器安全读取文件
    try:
        with open("./src/email_template/success_verify_email_ok.html", "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError as e:
        html_content = f"<h1>邮箱验证成功</h1><p>用户状态已更新为正常</p> [template missing - {e}]"
    
    return {
        "message": "邮箱验证成功，用户状态已更新为正常。",
        "html": html_content
    }