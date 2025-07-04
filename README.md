# FsPicArch

## 🚀 5分钟快速启动

```bash
# 克隆项目
git clone https://github.com/QiTan-Levi/FsPicArch.git
cd FsPicArch/Backend_FastAPI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload
```

访问 `http://localhost:8000/docs` 查看交互式API文档

## 🌟 功能矩阵

| 功能模块       | 状态 | 文档链接                  |
|----------------|------|---------------------------|
| 用户认证       | ✅   | [查看文档](#oauth2-api)   |
| 图片上传       | 🚧   | [查看文档](#upload-api)   |
| 数据统计       | ❌   | [计划中](#roadmap)        |

## ⚙️ 基础配置

```python
# config.py 关键配置
DB_CONFIG = {
    'host': '127.0.0.1',    # 数据库地址
    'port': 3306,           # 数据库端口
    'user': 'fspic_user',   # 数据库用户
    'password': 'your_strong_password',  # 必须修改！
    'database': 'fspicarch'
}

# JWT配置
JWT_SECRET = 'change_this_to_random_string'  # 必须修改！
TOKEN_EXPIRE_MINUTES = 1440  # 24小时
```

## 🤲 参与贡献
1. Fork 仓库
2. 创建分支 (`git checkout -b feat/your-feature`)
3. 提交代码 (`git commit -am 'Add awesome feature'`)
4. 推送分支 (`git push origin feat/your-feature`)
5. 创建 Pull Request

## 📜 开源许可
MIT Licensed | © 2025 FsPicArch Team
