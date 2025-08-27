import pymysql
from pymysql.cursors import DictCursor
from src.config import Config
import atexit
from typing import Optional, Tuple, Dict, Any, Union

class DatabaseService:
    """
    单例数据库服务类，自动管理MySQL连接，统一接口，支持自动/手动SQL
    """
    _instance = None
    _conn: Optional[pymysql.connections.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._init_connection()
            atexit.register(cls._instance._cleanup)
        return cls._instance

    def _init_connection(self):
        try:
            self._conn = pymysql.connect(
                **Config.DATABASE_CONFIG,
                cursorclass=DictCursor
            )
        except Exception as e:
            self._conn = None
            raise RuntimeError(f"数据库连接失败: {str(e)}")

    def _check_connection(self):
        if self._conn is None:
            self._init_connection()
        else:
            try:
                self._conn.ping(reconnect=True)
            except:
                self._conn.close()
                self._init_connection()

    def _cleanup(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except:
                pass
            finally:
                self._conn = None

    def execute(self,
                query: str = "",
                params: Union[tuple, dict, None] = None,
                auto: Optional[dict] = None) -> Any:
        """
        统一SQL执行接口，支持手动SQL和自动SQL（auto参数）
        auto: dict, 结构如：{
            "op": "create"|"read"|"update"|"delete",
            "table": "表名",
            "data": {字段:值},
            "where": {字段:值} 可选
        }
        """
        print(f"Executing SQL: {query} with params: {params} and auto: {auto}")
        self._check_connection()
        if self._conn is None:
            return False, "数据库连接未建立"
        try:
            # 自动SQL模式
            if auto:
                op = auto.get("op", "read")
                table = auto.get("table")
                data = auto.get("data", {})
                where = auto.get("where", {})
                if not table:
                    return False, "table参数缺失"
                if op == "create":
                    keys = ', '.join(data.keys())
                    placeholders = ', '.join(['%s'] * len(data))
                    sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
                    values = tuple(data.values())
                    with self._conn.cursor() as cursor:
                        cursor.execute(sql, values)
                        self._conn.commit()
                        return cursor.lastrowid
                elif op == "read":
                    sql = f"SELECT * FROM {table}"
                    values = ()
                    if where:
                        cond = ' AND '.join([f"{k}=%s" for k in where.keys()])
                        sql += f" WHERE {cond}"
                        values = tuple(where.values())
                    with self._conn.cursor() as cursor:
                        cursor.execute(sql, values)
                        return cursor.fetchall()
                elif op == "update":
                    set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
                    sql = f"UPDATE {table} SET {set_clause}"
                    values = tuple(data.values())
                    if where:
                        cond = ' AND '.join([f"{k}=%s" for k in where.keys()])
                        sql += f" WHERE {cond}"
                        values += tuple(where.values())
                    with self._conn.cursor() as cursor:
                        cursor.execute(sql, values)
                        self._conn.commit()
                        return cursor.rowcount
                elif op == "delete":
                    sql = f"DELETE FROM {table}"
                    values = ()
                    if where:
                        cond = ' AND '.join([f"{k}=%s" for k in where.keys()])
                        sql += f" WHERE {cond}"
                        values = tuple(where.values())
                    with self._conn.cursor() as cursor:
                        cursor.execute(sql, values)
                        self._conn.commit()
                        return cursor.rowcount
                else:
                    return False, f"不支持的自动操作类型: {op}"
            # 手动SQL模式
            else:
                with self._conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    sql_type = query.strip().split()[0].lower()
                    if sql_type == "select":
                        return cursor.fetchall()
                    elif sql_type == "insert":
                        self._conn.commit()
                        return cursor.lastrowid
                    elif sql_type in ("update", "delete"):
                        self._conn.commit()
                        return cursor.rowcount
                    else:
                        self._conn.commit()
                        return True
        except Exception as e:
            return False, f"SQL执行出错: {str(e)}"

# 全局单例实例
_db_service = DatabaseService()

def execute_sql(query: str = "", params: Union[tuple, dict, None] = None, auto: Optional[dict] = None) -> Any:
    """
    统一SQL接口，支持手动SQL和自动SQL（auto参数）
    手动SQL：execute_sql(query, params)
    自动SQL：execute_sql(auto = {"op": "create" | "read" | "update" | "delete", # 操作类型，分别对应增查改删
                                "table": "表名", # 操作的表名
                                "data": {字段:值}, # 用于插入/更新的数据（增/改时必填）
                                "where": {字段:值} # 查询/更新/删除的条件（可选，查/改/删时建议填写）
                                }
                        )
    """
    a= _db_service.execute(query, params, auto=auto)
    return a

__all__ = ["execute_sql"]