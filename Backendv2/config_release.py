import os
import hashlib
import jwt
from datetime import datetime, timedelta

class Config:
    SECRET_KEY = 'Your Secret Key'
    JWT_SECRET = 'Your Secret Key'
    '''
    你可以这样生成这两个密钥，得到结果后自己随意分配的得到两个密钥给 SECRET_KEY 和 JWT_SECRET。
    import secrets
    secrets.token_urlsafe(32) # 生成一个32位的随机字符串作为密钥
    '''
    JWT_ALGORITHM = 'HS256'
    TOKEN_EXPIRE_MINUTES = 30
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'aaa1234512345',
        'database': 'transportation'
    }
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    EMAIL_SERVER = 'smtp.exmail.qq.com'
    EMAIL_PORT = 465
    EMAIL_USER = 'Noreply@byinfo.cloud'
    EMAIL_PASS = '2aK2ZBArYFjKHEvC'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=Config.TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def decode_token(token):
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
