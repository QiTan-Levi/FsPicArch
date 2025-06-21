import pymysql
import json
import jwt
import os
import datetime
import smtplib
import logging
from email.mime.text import MIMEText
from email.header import Header
from flask import Flask, request, jsonify
from flask_cors import CORS
from jinja2 import Environment, FileSystemLoader


import config

app = Flask(__name__)
CORS(app)

#connect to database
db = pymysql.connect(
    host=config.Config.DB_CONFIG['host'],
    user=config.Config.DB_CONFIG['user'],
    password=config.Config.DB_CONFIG['password'],
    database=config.Config.DB_CONFIG['database']
)

#smtp prepare
email_user = config.Config.EMAIL_CONFIG['EMAIL_USER']
smtp = smtplib.SMTP_SSL(config.Config.EMAIL_CONFIG['EMAIL_SERVER'], config.Config.EMAIL_CONFIG['EMAIL_PORT'])
smtp.login(email_user, config.Config.EMAIL_CONFIG['EMAIL_PASS'])



#jinjia2 prepare
TEMPLATE_DIR = os.path.join(os.getcwd(), "templates")
from templates.TYPE_RC import TYPE_PARAMS, TYPE_SUBJECTS
template_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True
)

# logging prepare
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("FsPicArch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_dfnr_email(to, type, **kwargs):
    """
    发送默认不回复(DFNR)的通知邮件
    :param to: 收件人邮箱
    :param type: 通知类型（对应templates目录下的HTML文件名）
    :param kwargs: 不同类型对应的参数
    """
    # 校验通知类型
    if type not in TYPE_PARAMS:
        logger.error(f"不支持的通知类型: {type}")
        raise ValueError(f"不支持的通知类型: {type}")
    
    # 校验必填参数
    required_params = TYPE_PARAMS[type]
    for param in required_params:
        if param not in kwargs:
            logger.error(f"{type}类型缺少必填参数：{param}")
            raise ValueError(f"{type}类型缺少必填参数：{param}")
    
    # 加载并渲染HTML模板
    try:
        template = template_env.get_template(f"{type}.html")
        content = template.render(**kwargs)
    except Exception as e:
        logger.error(f"模板渲染失败: {e}", exc_info=True)
        raise RuntimeError("邮件模板渲染失败")
    
    # 通用邮件头设置
    msg = MIMEText(content, 'HTML', 'utf-8')
    msg['From'] = f"Byinfo Service <{email_user}>"
    msg['To'] = to
    msg['Subject'] = Header(TYPE_SUBJECTS[type], 'utf-8')
    
    # 发送邮件 (使用外部定义的smtp对象)
    try:
        smtp.sendmail(email_user, [to], msg.as_string())
        logger.info(f"邮件发送成功: 类型={type}, 收件人={to}")
    except Exception as e:
        logger.error(f"邮件发送失败: {e}", exc_info=True)
        raise RuntimeError("邮件发送失败，请稍后重试")


def debuger():
    send_dfnr_email("nninnos@163.com", "VERICODE", code="123456", user_id="123456789", expire_time="5分钟", current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    debuger()