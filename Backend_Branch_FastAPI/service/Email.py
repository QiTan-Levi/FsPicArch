# service/Email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import ssl
from typing import Optional
import atexit

class EmailService:
    _instance = None
    _server: Optional[smtplib.SMTP_SSL] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
            cls._instance._init_connection()
            # 注册退出时的清理函数
            atexit.register(cls._instance._cleanup)
        return cls._instance
    
    def _init_connection(self):
        """初始化SMTP连接"""
        try:
            context = ssl.create_default_context()
            self._server = smtplib.SMTP_SSL(
                Config.EMAIL_SERVER, 
                Config.EMAIL_PORT, 
                context=context
            )
            self._server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
        except Exception as e:
            self._server = None
            raise RuntimeError(f"邮件服务器连接失败: {str(e)}")
    
    def _check_connection(self):
        """检查连接是否有效"""
        if self._server is None:
            self._init_connection()
        else:
            try:
                self._server.noop()
            except:
                self._server.quit()
                self._init_connection()
    
    def _cleanup(self):
        """清理资源"""
        if self._server is not None:
            try:
                self._server.quit()
            except:
                pass
            finally:
                self._server = None
    
    def send(self, to_email: str, subject: str, content: str) -> tuple[bool, str]:
        """
        发送邮件
        
        参数:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容(支持HTML)
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            self._check_connection()
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{Config.EMAIL_USER_DISPLAY_NAME} <{Config.EMAIL_USER}>'
            msg['To'] = to_email
            msg.attach(MIMEText(content, 'html'))

            self._server.send_message(msg)
            return True, "邮件发送成功"

        except smtplib.SMTPAuthenticationError:
            error_msg = "认证失败！可能原因：\n1. 邮箱密码错误\n2. 需开启SMTP服务\n3. 需使用客户端专用密码"
            return False, error_msg
        except smtplib.SMTPException as e:
            return False, f"SMTP协议错误: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {str(e)}"

# 全局单例实例
_email_service = EmailService()

# 对外提供的简洁接口'''from service.Email import send_email'''
def send_email(to_email: str, subject: str, content: str) -> tuple[bool, str]:
    """发送邮件的高层接口"""
    return _email_service.send(to_email, subject, content)

# 测试代码
if __name__ == "__main__":
    # 测试发送邮件
    result, msg = send_email(
        "recipient@example.com",
        "测试邮件",
        "<h1>这是一封测试邮件</h1><p>HTML内容测试</p>"
    )
    print("发送成功" if result else f"发送失败: {msg}")