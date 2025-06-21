# service/Email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import ssl
from typing import Optional, Tuple, Dict, Union
import atexit
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class EmailService:
    _instance = None
    _server: Optional[smtplib.SMTP_SSL] = None
    _templates: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
            cls._instance._init_connection()
            cls._instance._load_templates()
            atexit.register(cls._instance._cleanup)
        return cls._instance
    
    def _init_connection(self):
        """Initialize SMTP connection"""
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
            raise RuntimeError(f"Failed to connect to mail server: {str(e)}")
    
    def _load_templates(self):
        """Load email templates from filesystem"""
        template_dir = Path(__file__).parent.parent / "src" / "email_template"
        
        # Load all HTML files in the template directory
        for template_file in template_dir.glob("*.html"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    self._templates[template_file.stem] = f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to load template {template_file.name}: {str(e)}")
    def _check_connection(self):
        """Check if connection is alive"""
        if self._server is None:
            self._init_connection()
        else:
            try:
                self._server.noop()
            except:
                self._server.quit()
                self._init_connection()
    
    def _cleanup(self):
        """Clean up resources"""
        if self._server is not None:
            try:
                self._server.quit()
            except:
                pass
            finally:
                self._server = None
    
    def send(
        self,
        to_email: str,
        subject: str,
        content: Union[str, Tuple[str, Dict[str, str]]]
    ) -> Tuple[bool, str]:
        """
        发送电子邮件（完整修复版）
        
        Args:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            content: 邮件内容，可以是：
                - 纯HTML字符串
                - 元组 (模板名称, 模板变量字典)
        
        Returns:
            (成功状态, 描述信息)
        """
        try:
            # 1. 验证收件人邮箱格式
            if not isinstance(to_email, str) or "@" not in to_email:
                return False, "收件人邮箱格式无效"
            
            # 2. 检查SMTP连接
            self._check_connection()
            if self._server is None:
                return False, "邮件服务器连接未建立"
            
            # 3. 准备邮件基础信息
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{Config.EMAIL_USER_DISPLAY_NAME} <{Config.EMAIL_USER}>'
            msg['To'] = to_email
            # 4. 处理不同类型的内容
            if isinstance(content, tuple):
                # 模板邮件处理
                if len(content) != 2:
                    return False, "模板参数格式错误，应为 (模板名称, 变量字典)"
                    
                template_name, template_vars = content
                
                # 验证模板变量必须是字典
                if not isinstance(template_vars, dict):
                    return False, "模板变量必须是字典类型"
                
                # 检查模板是否存在
                if template_name not in self._templates:
                    available = ", ".join(self._templates.keys())
                    return False, f"模板 '{template_name}' 不存在。可用模板: {available}"
                
                # 使用Jinja2渲染模板
                try:
                    env = Environment(loader=FileSystemLoader("src/email_template"))
                    template = env.get_template(f"{template_name}.html")
                    html_content = template.render(**template_vars)
                    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                except Exception as e:
                    return False, f"模板渲染失败: {str(e)}"
                    
            elif isinstance(content, str):
                # 纯HTML内容
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                return False, "邮件内容类型无效，必须是字符串或(模板名, 变量字典)"
            
            # 5. 发送邮件
            self._server.send_message(msg)
            return True, "邮件发送成功"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = ("SMTP认证失败！可能原因：\n"
                        "1. 邮箱密码错误\n"
                        "2. 未开启SMTP服务\n"
                        "3. 需要使用应用专用密码")
            return False, error_msg
            
        except smtplib.SMTPException as e:
            return False, f"SMTP协议错误: {str(e)}"
            
        except Exception as e:
            return False, f"发送邮件时出错: {str(e)}"

# Global singleton instance
_email_service = EmailService()

def send_email(
    to_email: str,
    subject: str,
    content: Union[str, Tuple[str, Dict[str, str]]]
) -> Tuple[bool, str]:
    """
    High-level interface for sending emails
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Email content, can be:
            - Raw HTML string
            - Tuple (template_name, template_vars)
    
    Returns:
        Tuple (success: bool, message: str)
    """
    return _email_service.send(to_email, subject, content)

# Test code
if __name__ == "__main__":
    # Test sending raw HTML email
    result, msg = send_email(
        "focuslevi@163.com",
        "Test Email",
        "<h1>This is a test email</h1><p>HTML content test</p>"
    )
    
    # Test sending template email
    template_vars = {
        "USER_NAME": "John Doe",
        "CODE": "123456",
        "NOTIFICATION_HEADER": "Your Verification Code",
        "NOTIFICATION_TYPE": "Security Alert"
    }
    result, msg = send_email(
        "focuslevi@163.com",
        "Verification Code",
        ("verify_code", template_vars)  # Uses verify_code.html template
    )
