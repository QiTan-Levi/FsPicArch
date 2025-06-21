from flask import Blueprint, request, jsonify
from config import hash_password, verify_password, generate_token, decode_token, Config
from core import get_db
import os
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_user_from_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return decode_token(token)

# 注册
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])
    email = data['email']

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registered successfully'})

# 登录
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user['password']):
        token = generate_token(user['id'])
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# 注销
@user_bp.route('/delete_account', methods=['DELETE'])
def delete_account():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id=%s", (user['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Account deleted'})

# 登出（前端直接丢弃Token）

# 上传图片
@user_bp.route('/upload', methods=['POST'])
def upload_image():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO images (user_id, filename, status) VALUES (%s, %s, %s)", (user['user_id'], filename, 'pending'))
        conn.commit()
        conn.close()
        return jsonify({'message': 'File uploaded'})
    return jsonify({'error': 'Invalid file'})

# 查看个人图片
@user_bp.route('/my_images', methods=['GET'])
def my_images():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM images WHERE user_id=%s", (user['user_id'],))
        images = cursor.fetchall()
    conn.close()
    return jsonify(images)

# 首页（展示所有已审核图片）
@user_bp.route('/homepage', methods=['GET'])
def homepage():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM images WHERE status='approved'")
        images = cursor.fetchall()
    conn.close()
    return jsonify(images)

# 搜索图片
@user_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    user_id = request.args.get('user_id', '')

    sql = "SELECT * FROM images WHERE 1=1"
    params = []

    if query:
        sql += " AND filename LIKE %s"
        params.append(f"%{query}%")
    if status:
        sql += " AND status=%s"
        params.append(status)
    if user_id:
        sql += " AND user_id=%s"
        params.append(user_id)

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        results = cursor.fetchall()
    conn.close()
    return jsonify(results)
