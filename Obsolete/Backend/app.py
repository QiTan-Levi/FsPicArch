import json
from configparser import ConfigParser
from re import U
from tkinter import image_names, image_types
from flask import Flask, request, make_response, jsonify , url_for
from flask_cors import CORS
import time
import uuid
import random
import os
from werkzeug.utils import secure_filename
from utils import (
    init_db_connections,
)
import mimetypes
import ast
from datetime import datetime, timedelta
import base64
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header

config = ConfigParser()
config.read('config.ini')

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": config.get('Address','Frontend_address'),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})

verification_codes={}

# 初始化数据库连接
mysql = init_db_connections()


smtp = smtplib.SMTP_SSL(config.get('Email', 'host'), config.get('Email', 'port'))
smtp.login(config.get('Email', 'user'), str(config.get('Email', 'password')))



# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "This is backend of Focus's Transportation Archive.\nPerhaps, you should use the frontend to visit the website."

@app.route('/api/images', methods=['GET'])  # 定义一个API路由，用于获取图片，只接受GET请求
def get_images():  # 定义获取图片的函数
    category = request.args.get('category', '全部')  # 从请求参数中获取类别，默认为'全部'
    search_query = request.args.get('search', '')  # 从请求参数中获取搜索关键词，默认为空字符串
    limit = request.args.get('limit', '20')  # 获取限制数量，默认为20张
    
    try:
        limit = int(limit)  # 将limit转换为整数
    except ValueError:
        limit = 20  # 如果转换失败，使用默认值20
    limit = 500
    cursor = mysql.cursor()  # 创建MySQL数据库游标
    base_query = """  # 定义基础SQL查询语句
        SELECT i.id, i.registration_number, i.file_type, i.aircraft_model, i.location, 
               i.image_description, i.upload_time, i.is_featured, i.user_id, 
               u.username, i.image_data,i.airline_operator,i.rating,i.views_num
        FROM images i
        JOIN users u ON i.user_id = u.id
        WHERE i.is_pending = 0
    """  # 选择未处于待审核状态的图片，并关联用户表获取用户名
    


    if category == '全部':  # 如果类别是'全部'
        if search_query:  # 如果有搜索关键词
            cursor.execute(base_query + " AND (i.aircraft_model LIKE %s OR i.image_description LIKE %s) ORDER BY i.upload_time DESC LIMIT %s", 
                         (f'%{search_query}%', f'%{search_query}%', limit))  # 执行SQL查询，搜索飞机型号或图片描述中包含关键词的图片
        else:  # 如果没有搜索关键词
            cursor.execute(base_query + " ORDER BY i.upload_time DESC LIMIT %s", (limit,))  # 执行基础SQL查询，获取所有图片，按上传时间降序排列，限制数量
    else:  # 如果类别不是'全部'
        if search_query:  # 如果有搜索关键词
            cursor.execute(base_query + " AND i.aircraft_model = %s AND (i.aircraft_model LIKE %s OR i.image_description LIKE %s) ORDER BY i.upload_time DESC LIMIT %s", 
                         (category, f'%{search_query}%', f'%{search_query}%', limit))  # 执行SQL查询，筛选特定飞机型号且包含搜索关键词的图片
        else:  # 如果没有搜索关键词
            cursor.execute(base_query + " AND i.aircraft_model = %s ORDER BY i.upload_time DESC LIMIT %s", (category, limit))  # 执行SQL查询，只筛选特定飞机型号的图片
    
    images = cursor.fetchall()  # 获取所有查询结果
    result = []  # 初始化结果列表
    for image in images:  # 遍历每一张图片
        # 将二进制图片数据编码为Base64字符串
        # Ensure image[9] is in bytes before encoding
        filedata_base64 = base64.b64encode(image[10]).decode('utf-8')  # 将图片二进制数据转换为Base64编码的字符串
        # print(str(image[:-3])+str(image[-2:]))
        result.append({  # 将图片信息添加到结果列表中
            'id': image[0],  # 图片ID
            'reg_number': image[1],  # 飞机注册号
            'airline': image[11],  # 航空公司
            'rating': int(image[12]),  # 评分
            'aircraft_model': image[3],  # 飞机型号
            'location': image[4],  # 拍摄地点
            'description': image[5],  # 图片描述
            'upload_time': image[6].strftime('%Y-%m-%d %H:%M:%S') if image[6] else None,  # 上传时间，格式化为字符串
            'user_id': image[8],  # 上传用户ID
            'username': image[9],  # 上传用户名
            'filename': image[2],  # 文件名
            'views': image[13],
            'content_type': 'image/jpeg',  # 内容类型，假设所有图片都是JPEG格式
            'filedata': filedata_base64  # 使用Base64编码的图片数据
        })
    
    return jsonify({  # 返回JSON格式的响应
        'status': 'success',  # 状态为成功
        'data': result  # 数据为处理后的图片列表
    })



@app.route('/api/pop', methods=['GET'])
def get_popular_images():
    cursor = mysql.cursor()  # 创建MySQL数据库游标
    likes_count_query = """
    SELECT 
        i.rating,
        i.registration_number,
        i.airline_operator,
        i.shooting_time,
        i.aircraft_model,
        i.image_data,
        i.likes_num,
        i.views_num,
        i.image_description,
        i.upload_time,
        i.location,
        u.username  -- Ensure this column is selected
    FROM 
        images i
    JOIN 
        comments c ON i.id = c.image_id
    JOIN 
        users u ON i.user_id = u.id  -- Add this join to include the users table
    WHERE 
        c.type = 1 AND -- 确保是点赞类型
        c.comment_time >= NOW() - INTERVAL 10 DAY
    GROUP BY 
        i.id
    ORDER BY 
        COUNT(c.id) DESC
    LIMIT 2;
    """
    cursor.execute(likes_count_query)  # 执行SQL查询，获取点赞数量最多的图片
    popular_images = cursor.fetchall()  # 获取所有查询结果

    result = []
    for image in popular_images:
        # Encode image_data to Base64
        image_data_base64 = base64.b64encode(image[5]).decode('utf-8')
        result.append({
            'rating': image[0],
            'registration_number': image[1],
            'airline_operator': image[2],
            'shooting_time': image[3],
            'aircraft_model': image[4],
            'likes_num': image[6],
            'views_num': image[7],
            'image_description': image[8],
            'upload_time': image[9].strftime('%Y-%m-%d %H:%M:%S') if image[9] else None,
            'location': image[10],
            'username': image[11],
            'image_data': image_data_base64
        })
    
    return jsonify({'status': 'success', 'data': result})

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': '没有文件被上传'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': '没有选择文件'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        content_type = mimetypes.guess_type(filename)[0]
        
        # 使用文件名作为文件ID
        # 获取表单数据
        username = request.form.get('username')
        
        # 初始化 cursor
        cursor = mysql.cursor()
        # print("接收到的表单数据:", request.form)  # 调试日志
        getting_user_id = cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        timezone = request.form.get('timeZone')

        registrationnumber = request.form.get('registrationNumber')
        aircraft_model = request.form.get('model')
        location = request.form.get('location')
        description = request.form.get('description')
        shooting_time = request.form.get('shootTime')
        flightNumber = request.form.get('flightNumber')
        airlineOperator = request.form.get('airlineOperator')
        image_typess = ast.literal_eval(request.form.getlist('categories')[0])
        weathers = ast.literal_eval(request.form.getlist('weatherConditions')[0])

        # Ensure image_typess is a list and join it into a string
        image_type_str = ','.join(image_typess) if image_typess else ''
        weather_str = ','.join(weathers) if weathers else ''

        # Debugging: Print SQL statement and parameters
        # print("SQL Statement: INSERT INTO images ...")
        # print("Parameters:", (user_id, shooting_time, timezone, registrationnumber,
        #                       aircraft_model, image_type_str, weather_str, description,
        #                       location, datetime.now(), 'jpg', file, flightNumber, airlineOperator))
        # 直接从上传的文件对象读取二进制数据
        file_data = file.read()

        # Insert into MySQL record
        cursor.execute("""
            INSERT INTO images (user_id, shooting_time, timezone, registration_number, 
                                aircraft_model, image_type, weather, image_description, 
                                location, upload_time, file_type, image_data, flight_number, airline_operator)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, shooting_time, timezone, registrationnumber,
            aircraft_model, image_type_str, weather_str, description,
            location, datetime.now(), 'jpg', file_data, flightNumber, airlineOperator))
        mysql.commit()
        return jsonify({'status': 'success', 'message': '图片上传成功'})
    return jsonify({'status': 'failed', 'message': '不支持的文件类型'})



@app.route('/api/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        cursor = mysql.cursor()
        cursor.execute("SELECT file_id, content_type FROM images WHERE file_id = %s", (file_id,))
        image = cursor.fetchone()
        if not image:
            return jsonify({'status': 'failed', 'message': '图片不存在'}), 404

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image[0])
        with open(file_path, 'rb') as file_obj:
            response = make_response(file_obj.read())
            response.mimetype = image[1]
            return response
    except Exception as e:
        return jsonify({'status': 'failed', 'message': '图片不存在'}), 404

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    email = email.lower()
    regis_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return {"status":"failed","message":"Username already exists."}
    
    # 读取 logo.svg 文件内容
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.svg')
    with open(logo_path, 'r', encoding='utf-8') as f:
        logo_content = f.read()

    cursor.execute("SELECT MAX(id) FROM users")
    last_id = cursor.fetchone()[0]
    id = last_id+1 if last_id else 1
    cursor.execute("INSERT INTO users (id, username, password, email, regis_time, status) VALUES (%s, %s, %s, %s, %s, 1)", 
                  (id, username, password, email, regis_time))
    mysql.commit()
    
    return {"status": "success", "message": "注册成功"}

def send_verification_email(email, code):
    with open('verifycode_email_template.html', 'r', encoding='utf-8') as f:
        html_content = f.read().replace('{{verification_code}}', code)
    try:
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['From'] = f"ByInfo Service <{config.get('Email', 'user')}>"
        msg['To'] = email
        msg['Subject'] = Header('ByInfo Service Picture Archive 验证码', 'utf-8')
        smtp.sendmail(config.get('Email', 'user'), [email], msg.as_string())  # Fixed line - changed ConfigParser.get to config.get
        print(f"验证码已发送到 {email}")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")

@app.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    data = request.json
    email = data['email']
    code = str(random.randint(100000, 999999))
    verification_codes[email] = {
        'code': code,
        'expire_time': time.time() + 300
    }
    send_verification_email(email, code)
    return {"status": "success", "message": "验证码已发送"}

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json

        if not data:
            return {"status": "failed", "message": "未接收到登录数据"}, 400

        # 检查必要的字段是否存在
        if not any(key in data for key in ['password', 'verificationCode']):
            return {"status": "failed", "message": "请提供密码或验证码"}, 400

        if 'password' in data:
            if not data.get('username'):
                return {"status": "failed", "message": "用户名不能为空"}, 400

            username = data['username']
            password = data['password']
            cursor = mysql.cursor()
            if re.match(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", username):
                username = username.lower()
                cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                            (username, password))
            else:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                            (username, password))
            user = cursor.fetchone()
            if not user:
                return {"status": "failed", "message": "用户名或密码错误"}, 401

            # 生成响应
            response = make_response({
                "status": "success", 
                "message": "登录成功",
                "data": {
                    "userId": user[0],
                    "username": user[1],
                    "userAvatar": user[3]  # 从数据库中获取头像信息
                }
            })

            # 设置 cookie
            user_info = {
                "userId": user[0],
                "username": user[1],
                "userAvatar": user[3]  # 添加 userAvatar
            }
            encoded_user_info = json.dumps(user_info)
            response.set_cookie('user-info', encoded_user_info, max_age=3600*24, path='/', httponly=False, samesite='Lax')
            response.set_cookie('token', str(uuid.uuid4()), max_age=3600*24, path='/', httponly=True, samesite='Lax')

            #记录最后登录时间
            cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(), user[0]))
            mysql.commit()

            return response

        elif 'verificationCode' in data:
            if not data.get('email'):
                return {"status": "failed", "message": "邮箱不能为空"}, 400

            email = data['email']
            code = data['verificationCode']

            if email not in verification_codes:
                return {"status": "failed", "message": "请先获取验证码"}, 401
            if time.time() > verification_codes[email]['expire_time']:
                return {"status": "failed", "message": "验证码已过期"}, 401
            if code != verification_codes[email]['code']:
                return {"status": "failed", "message": "验证码错误"}, 401

            del verification_codes[email]
            cursor = mysql.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return {"status": "failed", "message": "该邮箱未注册"}, 401

            # 生成token并设置cookie
            token = str(uuid.uuid4())
            user_info = {
                "userId": user[0],
                "username": user[1],
                "userAvatar": user[3]  # 从数据库中获取头像信息
            }
            response = make_response({
                "status": "success", 
                "message": "登录成功",
                "data": {
                    "userId": user[0],
                    "username": user[1],
                    "userAvatar": user_info["userAvatar"]
                }
            })
            encoded_user_info = json.dumps(user_info)
            response.set_cookie('user-info', encoded_user_info, max_age=3600*24, path='/', httponly=False, samesite='Lax')
            response.set_cookie('token', token, max_age=3600*24, path='/', httponly=True, samesite='Lax') # 建议 token 设置 httponly
            return response

        else:
            return {"status": "failed", "message": "无效的登录请求格式"}, 400

    except Exception as e:
        return {"status": "failed", "message": f"登录失败: {str(e)}"}, 500

@app.route('/api/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': '没有文件被上传'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': '没有选择文件'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        avatar_url = url_for('uploaded_file', filename=filename)
        user_id = request.form.get('user_id')
        cursor = mysql.cursor()
        cursor.execute("""
            UPDATE users SET avatar_url = %s WHERE id = %s
        """, (avatar_url, user_id))
        mysql.commit()
        return jsonify({'status': 'success', 'message': '头像上传成功', 'avatar_url': avatar_url})
    return jsonify({'status': 'failed', 'message': '不支持的文件类型'})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)