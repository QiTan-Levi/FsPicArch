# SQLsvc.py
import pymysql
from pymysql.cursors import DictCursor
from typing import Generator
from config import Config

class DatabaseService:
    @staticmethod
    def get_db_connection() -> Generator:
        """获取数据库连接"""
        connection = pymysql.connect(
            **Config.DB_CONFIG,
            cursorclass=DictCursor
        )
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def execute_query(conn, query: str, params: tuple = None):
        """执行查询并返回结果"""
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    @staticmethod
    def execute_update(conn, query: str, params: tuple = None):
        """执行更新操作并提交"""
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def get_user_by_username(conn, username: str):
        """根据用户名获取用户"""
        return DatabaseService.execute_query(
            conn,
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )

    @staticmethod
    def create_user(conn, user_data: dict):
        """创建新用户"""
        query = """
        INSERT INTO users 
        (username, password, email, avatar, bio, unique_identifier) 
        VALUES (%s, %s, %s, %s, %s, UUID())
        """
        params = (
            user_data['username'],
            user_data['password'],
            user_data['email'],
            user_data.get('avatar'),
            user_data.get('bio')
        )
        DatabaseService.execute_update(conn, query, params)
        
        # 返回新创建的用户
        return DatabaseService.execute_query(
            conn,
            """
            SELECT id, username, email, avatar, approved_images_count, 
                   likes_received_count, uploads_count, account_level, registration_time
            FROM users WHERE username = %s
            """,
            (user_data['username'],)
        )