@echo off
rem 进入前端目录并安装依赖，然后启动开发服务器
cd frontend
start cmd /k "npm install && npm run dev"

rem 新建一个窗口执行后端项目
start cmd /k "cd ../Backend && python app.py"    