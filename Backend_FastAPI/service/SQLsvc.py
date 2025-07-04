# SQLsvc.py
import pymysql
from pymysql.cursors import DictCursor
from typing import Generator
from config import Config

class DatabaseService:
    """
    数据库服务类，提供与MySQL数据库交互的各种静态方法
    """
    
    @staticmethod
    def get_db_connection() -> Generator:
        """
        获取数据库连接生成器
        
        使用yield实现生成器模式，确保连接在使用后能正确关闭
        返回: 数据库连接生成器
        """
        # 根据配置创建数据库连接，使用DictCursor返回字典格式的结果
        connection = pymysql.connect(
            **Config.DATABASE_CONFIG,
            cursorclass=DictCursor
        )
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def execute_query(conn, query: str, params: tuple = None):
        """
        执行查询SQL语句
        
        参数:
            conn: 数据库连接对象
            query: SQL查询语句
            params: SQL参数元组(可选)
        返回: 查询结果列表
        """
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())  # 执行查询，如果没有参数则使用空元组
            return cursor.fetchall()  # 获取所有结果

    @staticmethod
    def execute_update(conn, query: str, params: tuple = None):
        """
        执行更新SQL语句(INSERT/UPDATE/DELETE)
        
        参数:
            conn: 数据库连接对象
            query: SQL更新语句
            params: SQL参数元组(可选)
        返回: 受影响的行数
        """
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())  # 执行更新
            conn.commit()  # 提交事务
            return cursor.rowcount  # 返回受影响的行数

    @staticmethod
    def get_user_by_username(conn, username: str):
        """
        根据用户名查询用户信息
        
        参数:
            conn: 数据库连接对象
            username: 要查询的用户名
        返回: 用户信息列表(如果没有则为空列表)
        """
        return DatabaseService.execute_query(
            conn,
            "SELECT * FROM users WHERE username = %s",  # 查询用户所有字段
            (username,)
        )

    @staticmethod
    def create_user(conn, user_data: dict):
        """
        创建新用户
        
        参数:
            conn: 数据库连接对象
            user_data: 包含用户信息的字典，应有username,password,email等字段
        返回: 新创建的用户信息(不包含敏感信息)
        """
        # 插入用户SQL，使用UUID()生成唯一标识符
        query = """
        INSERT INTO users 
        (username, password, email, avatar, bio, unique_identifier) 
        VALUES (%s, %s, %s, %s, %s, UUID())
        """
        # 准备插入参数
        params = (
            user_data['username'],
            user_data['password'],
            user_data['email'],
            user_data.get('avatar'),  # 可选字段使用get方法
            user_data.get('bio')      # 可选字段使用get方法
        )
        # 执行插入
        DatabaseService.execute_update(conn, query, params)
        
        # 返回新创建的用户信息(不包含密码等敏感字段)
        return DatabaseService.execute_query(
            conn,
            """
            SELECT id, username, email, avatar, approved_images_count, 
                   likes_received_count, uploads_count, account_level, registration_time
            FROM users WHERE username = %s
            """,
            (user_data['username'],)
        )