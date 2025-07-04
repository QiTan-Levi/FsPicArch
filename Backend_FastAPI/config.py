# config.py
class Config:
    """应用配置类，包含所有系统配置参数"""

    # ==================== 应用安全配置 ====================
    # 加密密钥配置
    APP_SECRET_KEY = 'D0USI4Pzlc5yE6Av7C3hDGvbfleilDwSApJJK73K_0E'  # Flask应用密钥
    JWT_SECRET_KEY = 'nH1y2RiCdI_uK6iH_JnQcrhYQDwNhHj6XQm5-hm0RdE'  # JWT令牌密钥
    JWT_ALGORITHM = 'HS256'  # JWT加密算法
    TOKEN_EXPIRE_MINUTES = 30  # JWT令牌过期时间(分钟)

    # ==================== 数据库配置 ====================
    DATABASE_CONFIG = {  
        'host': 'localhost',      # 数据库主机地址
        'user': 'root',           # 数据库用户名
        'password': 'aaa1234512345',  # 数据库密码
        'database': 'fspicarch'   # 数据库名称
    }

    # ==================== 文件上传配置 ====================
    
    # 文件类型详细配置
    FILE_TYPE_RULES = {
        "avatar": {  # 头像文件规则
            "mime_types": ["image/jpeg", "image/png"],  # 允许的MIME类型
            "extensions": ["jpg", "jpeg", "png"],       # 允许的扩展名
            "max_size": 2 * 1024 * 1024,               # 最大2MB
            "is_image": True                           # 是否为图片
        },
        "general": {  # 普通文件规则
            "mime_types": ["image/jpeg", "image/png"],
            "extensions": ["jpg", "jpeg", "png"],
            "max_size": 5 * 1024 * 1024,               # 最大5MB
            "is_image": True
        }
    }

    # ==================== 邮件服务配置 ====================
    SMTP_SERVER = 'smtp.exmail.qq.com'  # SMTP服务器地址
    SMTP_PORT = 465                     # SMTP端口(SSL)
    SMTP_USERNAME = 'Noreply@byinfo.cloud'  # 发件邮箱
    SMTP_DISPLAY_NAME = 'Byinfo Group'   # 发件人显示名称
    SMTP_PASSWORD = 'RNKPwVhk49Bw4jR8'   # SMTP密码

    # ==================== 静态资源配置 ====================
    STATIC_FILES_DIR = 'static'  # 静态文件目录

    # ==================== 调试与错误处理 ====================
    DEBUG_MODE = True  # 是否启用详细错误信息-未启用

    # ==================== 邮箱验证配置 ====================
    EMAIL_VERIFICATION_CODE_LENGTH = 6  # 验证码长度-未启用
    EMAIL_CODE_NUMERIC_ONLY = True     # 是否仅使用数字验证码-未启用
    EMAIL_CODE_EXPIRE_MINUTES = 10     # 验证码有效期(分钟)