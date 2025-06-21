# utils/File.py
import os
import uuid
from fastapi import UploadFile, HTTPException
from fastapi import status
from PIL import Image
import io
from typing import List, Optional
from config import Config

class FileService:
    @staticmethod
    async def handle_file_upload(
        file: UploadFile,
        file_type: str,
        upload_dir: str,
        old_files: Optional[List[str]] = None,
        fixed_filename: Optional[str] = None
    ) -> str:
        """
        通用文件上传处理器
        
        参数:
            file: UploadFile - 上传的文件对象
            file_type: str - 文件类型(对应config中的配置)
            upload_dir: str - 上传目录
            old_files: Optional[List[str]] - 需要删除的旧文件列表
            fixed_filename: Optional[str] - 固定文件名(不包含扩展名)
            
        返回:
            str - 存储的文件路径(相对路径)
        """
        # 获取配置
        config = Config.ALLOWED_FILE_TYPES.get(file_type)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型配置: {file_type}"
            )
        
        # 验证文件类型和扩展名
        FileService._validate_file(file, config)
        
        # 读取文件内容
        contents = await file.read()
        
        # 验证文件大小
        if len(contents) > config["max_size"]:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小不能超过 {config['max_size'] // (1024 * 1024)}MB"
            )
        
        # 如果是图片，验证确实是有效图片
        if config["is_image"]:
            FileService._validate_image(contents)
        
        # 生成文件名
        file_ext = file.filename.split('.')[-1].lower()
        filename = FileService._generate_filename(file_ext, fixed_filename)
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 删除旧文件
        if old_files:
            FileService._delete_old_files(old_files)
        
        # 保存新文件
        file_path = os.path.join(upload_dir, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"保存文件时出错: {str(e)}"
            )
        
        return os.path.join(upload_dir, filename)
    
    @staticmethod
    def _validate_file(file: UploadFile, config: dict):
        """验证文件类型和扩展名"""
        if file.content_type not in config["mime_types"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file.content_type}"
            )
        
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in config["extensions"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的文件扩展名: {file_ext}"
            )
    
    @staticmethod
    def _validate_image(contents: bytes):
        """验证是否是有效的图片文件"""
        try:
            Image.open(io.BytesIO(contents)).verify()
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的图片文件"
            )
    
    @staticmethod
    def _generate_filename(file_ext: str, fixed_filename: Optional[str] = None) -> str:
        """
        生成文件名
        如果有固定文件名，则使用固定文件名；否则生成UUID
        """
        if fixed_filename:
            return f"{fixed_filename}.{file_ext}"
        return f"{uuid.uuid4().hex}.{file_ext}"
    
    @staticmethod
    def _delete_old_files(old_files: List[str]):
        """删除旧文件"""
        for old_file in old_files:
            old_path = old_file.lstrip('/')
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except:
                pass  # 忽略删除错误