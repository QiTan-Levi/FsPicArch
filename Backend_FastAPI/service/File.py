import os
import uuid
from PIL import Image
import io
from typing import List, Optional, Dict, Any, Union
from fastapi import UploadFile
from src.config import Config
from service.SQLsvc import execute_sql
import atexit

class FileService:
    """
    单例文件服务类，提供文件CRUD操作，自动管理资源
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileService, cls).__new__(cls)
            atexit.register(cls._instance._cleanup)
        return cls._instance

    def _cleanup(self):
        pass

    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """查询用户权限组和状态"""
        result = execute_sql(auto={
            "op": "read",
            "table": "users",
            "where": {"id": user_id}
        })
        if isinstance(result, list) and result:
            user = result[0]
            return {
                "permission_group": user.get("permission_group"),
                "status": user.get("status")
            }
        return {}

    def _get_file_permission(self, file_path: str) -> Dict[str, Any]:
        """查询文件权限和权限组"""
        result = execute_sql(auto={
            "op": "read",
            "table": "files",
            "where": {"file_path": file_path}
        })
        if isinstance(result, list) and result:
            file = result[0]
            return {
                "file_permission": file.get("file_permission"),
                "file_permission_group": file.get("file_permission_group"),
                "user_id": file.get("user_id"),
                "status": file.get("status")
            }
        return {}

    def _check_permission(self, user_id: str, op: str, file_info: Dict[str, Any]) -> bool:
        """
        综合用户和文件权限核查
        """
        user = self._get_user_info(user_id)
        # 用户必须存在且状态正常
        if not user or user.get("status") not in [1, 2, 3]:
            print(user)
            print(1)
            return False

        # 文件相关权限判断
        file_path = file_info.get("target_file") or file_info.get("file_path")
        file_perm = self._get_file_permission(file_path) if file_path else {}

        # 上传时只校验用户权限组
        if op == "create":
            # 可根据 file_info["file_type"] 做更细致判断
            print(2)
            return user.get("permission_group") == 'user' or 'admin' and user.get("status") in [1, 2, 3]
        # 其他操作需校验文件权限
        if file_perm:
            # 文件必须正常
            if file_perm.get("status") != 1:
                print(3)
                return False
            # 用户是文件所有者或在文件权限组内或在文件权限列表
            if (file_perm.get("user_id") == int(user_id) or
                user.get("permission_group") == file_perm.get("file_permission_group") or
                (file_perm.get("file_permission") and str(user_id) in str(file_perm.get("file_permission")))):
                print(4)
                return True
            print(5)
            return False
        # 没有文件权限信息时，默认拒绝
        print(6)
        return False

    async def execute(self, op: str, user_id: str, file: Optional[UploadFile] = None,
                file_info: Optional[Dict[str, Any]] = None,
                old_files: Optional[List[str]] = None,
                fixed_filename: Optional[str] = None) -> Any:

        if not file_info or "file_type" not in file_info or "upload_dir" not in file_info:
            return {'error': 'file_info参数缺失'}
        if not self._check_permission(user_id, op, file_info):
            return {'error': '无操作权限'}
        config = Config.FILE_TYPE_RULES.get(file_info["file_type"])
        if not config:
            return {'error': f"不支持的文件类型: {file_info['file_type']}"}

        if op == "create":
            contents = file and (await file.read())
            if not contents:
                return {'error': '文件内容为空'}
            if len(contents) > config["max_size"]:
                return {'error': '文件过大'}
            if config["is_image"]:
                try:
                    Image.open(io.BytesIO(contents)).verify()
                except:
                    return {'error': '无效图片'}
            file_ext = file.filename.split('.')[-1].lower()
            # ident_code 生成：base64前50位+HEX CRC32
            import base64, binascii
            b64 = base64.b64encode(contents).decode('utf-8')[:50]
            crc = format(binascii.crc32(contents) & 0xffffffff, '08x')
            ident_code = f"{b64}_{crc}"
            # hash 可用 ident_code 的 CRC32 或 uuid4
            hash_part = uuid.uuid4().hex[:8]
            related_id = file_info.get("related_id", "unknown")
            filename = f"{related_id}_{crc}_{hash_part}.{file_ext}"
            os.makedirs(file_info["upload_dir"], exist_ok=True)
            if old_files:
                for old_file in old_files:
                    # old_file 可能是 /static/avatar/2.jpg 或 static/avatar/2.jpg
                    old_path = old_file.replace('/', os.sep).lstrip(os.sep)
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        print(f"删除旧头像失败: {e}")
            file_path = os.path.join(file_info["upload_dir"], filename)
            try:
                with open(file_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                return {'error': f"保存文件时出错: {str(e)}"}

            # ident_code 生成：base64前50位+HEX CRC32
            import base64, binascii
            b64 = base64.b64encode(contents).decode('utf-8')[:50]
            crc = format(binascii.crc32(contents) & 0xffffffff, '08x')
            ident_code = f"{b64}_{crc}"

            # 写入files表，支持related_id和related_table
            file_data = {
                "user_id": int(user_id),
                "ident_code": ident_code,
                "file_name": filename,
                "file_path": file_path,
                "file_type": file_info.get("file_type"),
                "file_tag": file_info.get("file_tag"),
                "file_permission": file_info.get("file_permission"),
                "file_permission_group": file_info.get("file_permission_group"),
                "status": 1
            }
            # 新增关联字段
            if "related_id" in file_info:
                file_data["related_id"] = file_info["related_id"]
            if "related_table" in file_info:
                file_data["related_table"] = file_info["related_table"]

            execute_sql(auto={
                "op": "create",
                "table": "files",
                "data": file_data
            })
            return {'success': True, 'file_path': file_path, 'ident_code': ident_code}

        elif op == "read":
            target_file = file_info.get("target_file")
            if not target_file or not os.path.exists(target_file):
                return {'error': '文件不存在'}
            # 可根据files表做更多信息返回
            with open(target_file, "rb") as f:
                return {'success': True, 'content': f.read()}

        elif op == "update":
            result = await self.execute("create", user_id, file, file_info, old_files, fixed_filename)
            if 'error' in result:
                return result
            return {'success': True, 'file_path': result['file_path']}

        elif op == "delete":
            target_file = file_info.get("target_file")
            if not target_file or not os.path.exists(target_file):
                return {'error': '文件不存在'}
            try:
                os.remove(target_file)
                # 更新files表状态
                execute_sql(auto={
                    "op": "update",
                    "table": "files",
                    "data": {"status": 0},
                    "where": {"file_path": target_file}
                })
                return {'success': True}
            except Exception as e:
                return {'error': f"删除文件失败: {str(e)}"}
        else:
            return {'error': f"不支持的操作类型: {op}"}

# 单例实例
_file_service = FileService()

# 暴露函数
async def file_service_execute(
    op: str, 
    user_id: str, 
    file: Optional[UploadFile] = None,
    file_info: Optional[Dict[str, Any]] = None,
    old_files: Optional[List[str]] = None,
    fixed_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    对外暴露的唯一文件服务接口
    返回格式:
      - 成功: {'success': True, 'data': ...}
      - 失败: {'error': '错误原因'}
    """
    result = await _file_service.execute(op, user_id, file, file_info, old_files, fixed_filename)
    return result

__all__ = ['file_service_execute']