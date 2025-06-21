import os
import hashlib
import jwt
from datetime import datetime, timedelta

class Config:
    SECRET_KEY = 'D0USI4Pzlc5yE6Av7C3hDGvbfleilDwSApJJK73K_0E'
    JWT_SECRET = 'nH1y2RiCdI_uK6iH_JnQcrhYQDwNhHj6XQm5-hm0RdE'
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
