from flask import Flask, request, jsonify, send_from_directory
import pymysql
import os
from config import Config
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

from flask_cors import CORS
CORS(app)

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Database connection
def get_db():
    return pymysql.connect(
        host=Config.DB_CONFIG['host'],
        user=Config.DB_CONFIG['user'],
        password=Config.DB_CONFIG['password'],
        database=Config.DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    from user import user_bp
    app.register_blueprint(user_bp)
    app.run(debug=True)
