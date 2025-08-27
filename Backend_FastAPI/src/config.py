# config.py
class Config:
    """应用类"""

    # ==================== 应用安全配置 ====================
    # 加密密钥配置
    APP_SECRET_KEY = 'D0USI4Pzlc5yE6Av7C3hDGvbfleilDwSApJJK73K_0E'  # Flask应用密钥
    JWT_SECRET_KEY = 'nH1y2RiCdI_uK6iH_JnQcrhYQDwNhHj6XQm5-hm0RdE'  # JWT令牌密钥
    JWT_ALGORITHM = 'HS256'  # JWT加密算法
    TOKEN_EXPIRE_MINUTES = 30  # JWT令牌过期时间(分钟)

    # ==================== 数据库配置 ====================
    DATABASE_CONFIG = {  
        'host': 'localhost',      # 数据库主机地址
        'user': 'fapicarch2025_pr',           # 数据库用户名
        'password': 'fs2025pic$hr_ot^as@#st5',  # 数据库密码
        'database': 'fspicarch'   # 数据库名称
    }

    # ==================== 文件上传配置 ====================
    
    # 文件类型详细配置
    FILE_TYPE_RULES = {
        "avatar": {  # 头像文件规则
            "mime_types": ["image/jpeg", "image/png"],  # 允许的MIME类型
            "extensions": ["jpg", "jpeg", "png"],       # 允许的扩展名
            "max_size": 100 * 1024 * 1024,               # 最大2MB
            "is_image": True                           # 是否为图片
        },
        "general": {  # 普通文件规则
            "mime_types": ["image/jpeg", "image/png"],
            "extensions": ["jpg", "jpeg", "png"],
            "max_size": 1000 * 1024 * 1024,               # 最大5MB
            "is_image": True
        }
    }

    # ==================== 邮件服务配置 ====================
    SMTP_SERVER = 'smtp.exmail.qq.com'  # SMTP服务器地址
    SMTP_PORT = 465                     # SMTP端口(SSL)
    SMTP_USERNAME = 'Noreply@byinfo.cloud'  # 发件邮箱
    SMTP_DISPLAY_NAME = 'Byinfo Group'   # 发件人显示名称
    SMTP_PASSWORD = 'RNKPwVhk49Bw4jR8'   # SMTP密码

    """偏好类"""
    
    # ==================== 静态资源配置 ====================
    STATIC_FILES_DIR = 'static'  # 静态文件目录
    MAIN_SERVICE_PORT = 8000     # 主服务端口

    # ==================== 调试与错误处理 ====================
    DEBUG_MODE = False  # 是否启用详细错误信息-未启用

    # ==================== 管理员/所有者自己 ====================
    ADMIN_EMAIL = 'focuslevi@163.com'  # 管理员邮箱

    # ==================== 前后端URL配置 ====================
    FRONTEND_URL = 'http://localhost:3000'  # 前端应用URL
    BACKEND_URL = 'http://localhost:8000'   # 后端应用URL

    # ==================== 邮箱验证配置 ====================
    SECONDARY_ENHANCED_EMAIL_VERIFICATION = False  # 是否启用二类增强邮箱验证方案
    '''
    # 二类增强方案什么意思?
    - user.py中的 varify_email_newuser BY_POST方法可以看到, URL中有UUID 在request body里面有CODE。这两个值必须同时匹配才能通过验证，这就要求你在前端注册完成后就要让用户看到CODE，然后再要设计一个页面比如 http://Frontend/verify_email?uuid=xxx 加到Email里，用户点击链接后打开这个页面，页面上有个输入框让用户输入CODE，前端再把UUID和CODE一起POST到后端进行验证。
    - 注册请求给后端 --> 后端生成UUID和CODE，把CODE发给前端，发一个EMAIL有http://Frontend/verify_email?uuid=xxx --> 前端把CODE展示给用户 --> 用户去邮箱点击链接打开前端验证页面 --> 用户输入CODE提交 --> 前端把UUID和CODE一起POST给后端验证
    
    # 如果是False
    - 那么只要用户点击邮件中的链接就能通过验证，把CODE去掉了
    - 注册请求给后端 --> 后端生成UUID，把UUID发给前端，发一个EMAIL有http://Backend/verify_email/uuid --> 用户去邮箱点击链接发送get --> 后端验证通过
    '''