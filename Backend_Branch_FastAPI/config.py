# config.py
class Config:
    # Application configurations
    SECRET_KEY = 'D0USI4Pzlc5yE6Av7C3hDGvbfleilDwSApJJK73K_0E'
    JWT_SECRET = 'nH1y2RiCdI_uK6iH_JnQcrhYQDwNhHj6XQm5-hm0RdE'
    JWT_ALGORITHM = 'HS256'
    TOKEN_EXPIRE_MINUTES = 30

    # 3rd party service configurations
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'aaa1234512345',
        'database': 'fspicarch'
    }
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    EMAIL_SERVER = 'smtp.exmail.qq.com'
    EMAIL_PORT = 465
    EMAIL_USER = 'Noreply@byinfo.cloud'
    EMAIL_USER_DISPLAY_NAME = 'Byinfo Group'
    EMAIL_PASS = 'RNKPwVhk49Bw4jR8'
    
    # Statics and media directories
    STATIC_DIR = 'static'    

