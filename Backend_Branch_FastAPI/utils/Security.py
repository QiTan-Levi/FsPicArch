# security.py
import hashlib
import jwt
from datetime import datetime, timedelta
from config import Config

def hash_password(password: str) -> str:
    """使用SHA-256算法哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配哈希值"""
    return hash_password(plain_password) == hashed_password

def generate_token(user_id: str) -> str:
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=Config.TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None