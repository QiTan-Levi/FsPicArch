# service/Email.py

# 导入必要的库
import smtplib  # SMTP协议库
from email.mime.text import MIMEText  # 构建邮件正文
from email.mime.multipart import MIMEMultipart  # 构建多部分邮件
from config import Config  # 配置文件
import ssl  # SSL加密
from typing import Optional, Tuple, Dict, Union  # 类型提示
import atexit  # 程序退出时的清理
from pathlib import Path  # 路径操作
from jinja2 import Environment, FileSystemLoader  # 模板引擎

class EmailService:
    # 单例模式实现
    _instance = None
    # SMTP服务器连接
    _server: Optional[smtplib.SMTP_SSL] = None
    # 存储加载的邮件模板
    _templates: Dict[str, str] = {}
    
    def __new__(cls):
        """单例模式实现，确保全局只有一个EmailService实例"""
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
            # 初始化SMTP连接
            cls._instance._init_connection()
            # 加载邮件模板
            cls._instance._load_templates()
            # 注册程序退出时的清理函数
            atexit.register(cls._instance._cleanup)
        return cls._instance
    
    def _init_connection(self):
        """初始化SMTP SSL连接"""
        try:
            # 创建默认SSL上下文
            context = ssl.create_default_context()
            # 建立SMTP SSL连接
            self._server = smtplib.SMTP_SSL(
                Config.SMTP_SERVER,  # SMTP服务器地址
                Config.SMTP_PORT,  # SMTP端口
                context=context  # SSL上下文
            )
            # 登录SMTP服务器
            self._server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        except Exception as e:
            self._server = None
            raise RuntimeError(f"Failed to connect to mail server: {str(e)}")
    
    def _load_templates(self):
        """从文件系统加载所有HTML邮件模板"""
        # 构建模板目录路径（假设模板位于src/email_template目录下）
        template_dir = Path(__file__).parent.parent / "src" / "email_template"
        
        # 遍历目录下所有HTML文件
        for template_file in template_dir.glob("*.html"):
            try:
                # 读取模板文件内容并存储到字典中
                with open(template_file, "r", encoding="utf-8") as f:
                    # 使用文件名（不带扩展名）作为键
                    self._templates[template_file.stem] = f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to load template {template_file.name}: {str(e)}")

    def _check_connection(self):
        """检查SMTP连接是否有效，必要时重新连接"""
        if self._server is None:
            # 如果连接不存在，则初始化
            self._init_connection()
        else:
            try:
                # 发送NOOP命令测试连接
                self._server.noop()
            except:
                # 如果测试失败，关闭旧连接并重新建立
                self._server.quit()
                self._init_connection()
    
    def _cleanup(self):
        """程序退出时清理资源"""
        if self._server is not None:
            try:
                # 优雅地关闭SMTP连接
                self._server.quit()
            except:
                pass  # 忽略退出时的异常
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
        
        参数:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            content: 邮件内容，可以是以下两种形式之一：
                1. 纯HTML字符串
                2. 元组 (模板名称, 模板变量字典)
        
        返回:
            元组 (成功状态, 描述信息)
        """
        try:
            # 1. 验证收件人邮箱格式
            if not isinstance(to_email, str) or "@" not in to_email:
                return False, "收件人邮箱格式无效"
            
            # 2. 检查SMTP连接状态
            self._check_connection()
            if self._server is None:
                return False, "邮件服务器连接未建立"
            
            # 3. 构建邮件基础信息
            msg = MIMEMultipart('alternative')  # 创建多部分邮件
            msg['Subject'] = subject  # 邮件主题
            msg['From'] = f'{Config.SMTP_DISPLAY_NAME} <{Config.SMTP_USERNAME}>'  # 发件人
            msg['To'] = to_email  # 收件人
            
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
                    # 创建Jinja2环境
                    env = Environment(loader=FileSystemLoader("src/email_template"))
                    # 获取模板
                    template = env.get_template(f"{template_name}.html")
                    # 渲染模板
                    html_content = template.render(**template_vars)
                    # 添加HTML内容到邮件
                    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                except Exception as e:
                    return False, f"模板渲染失败: {str(e)}"
                    
            elif isinstance(content, str):
                # 纯HTML内容直接附加到邮件
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                return False, "邮件内容类型无效，必须是字符串或(模板名, 变量字典)"
            
            # 5. 发送邮件
            self._server.send_message(msg)
            return True, "邮件发送成功"
            
        except smtplib.SMTPAuthenticationError:
            # SMTP认证错误处理
            error_msg = ("SMTP认证失败！可能原因：\n"
                        "1. 邮箱密码错误\n"
                        "2. 未开启SMTP服务\n"
                        "3. 需要使用应用专用密码")
            return False, error_msg
            
        except smtplib.SMTPException as e:
            # SMTP协议错误处理
            return False, f"SMTP协议错误: {str(e)}"
            
        except Exception as e:
            # 其他异常处理
            return False, f"发送邮件时出错: {str(e)}"

# 全局单例实例
_email_service = EmailService()

def send_email(
    to_email: str,
    subject: str,
    content: Union[str, Tuple[str, Dict[str, str]]]
) -> Tuple[bool, str]:
    """
    发送电子邮件的高级接口
    
    参数:
        to_email: 收件人邮箱地址
        subject: 邮件主题
        content: 邮件内容，可以是：
            - 原始HTML字符串
            - 元组 (模板名称, 模板变量字典)
    
    返回:
        元组 (成功状态: bool, 消息: str)
    """
    return _email_service.send(to_email, subject, content)

# 测试代码
if __name__ == "__main__":
    # 测试发送纯HTML邮件
    result, msg = send_email(
        "focuslevi@163.com",
        "Test Email",
        "<h1>This is a test email</h1><p>HTML content test</p>"
    )
    print(f"测试结果: {result}, 消息: {msg}")
    
    # 测试发送模板邮件
    template_vars = {
        "USER_NAME": "John Doe",
        "CODE": "123456",
        "NOTIFICATION_HEADER": "Your Verification Code",
        "NOTIFICATION_TYPE": "Security Alert"
    }
    result, msg = send_email(
        "focuslevi@163.com",
        "Verification Code",
        ("verify_code", template_vars)  # 使用verify_code.html模板
    )
    print(f"模板邮件测试结果: {result}, 消息: {msg}")