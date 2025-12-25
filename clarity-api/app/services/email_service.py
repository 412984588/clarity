"""邮件服务"""
import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """发送密码重置邮件"""
    if not settings.smtp_enabled:
        logger.warning("SMTP is disabled, password reset email not sent")
        return False

    reset_link = f"{settings.frontend_url}/auth/reset?token={reset_token}"

    message = EmailMessage()
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from}>"
    message["To"] = to_email
    message["Subject"] = "密码重置 - Clarity"

    message.set_content(f"""
您好，

您请求重置 Clarity 账户的密码。请点击以下链接重置密码：

{reset_link}

此链接将在30分钟后过期。

如果您没有请求重置密码，请忽略此邮件。

Clarity 团队
    """)

    message.add_alternative(f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #4CAF50;">密码重置</h2>
      <p>您好，</p>
      <p>您请求重置 Clarity 账户的密码。</p>
      <p style="margin: 30px 0;">
        <a href="{reset_link}" 
           style="background-color: #4CAF50; 
                  color: white; 
                  padding: 12px 24px; 
                  text-decoration: none; 
                  border-radius: 5px;
                  display: inline-block;">
          重置密码
        </a>
      </p>
      <p style="color: #666; font-size: 14px;">此链接将在30分钟后过期。</p>
      <p style="color: #666; font-size: 14px;">如果您没有请求重置密码，请忽略此邮件。</p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
      <p style="color: #999; font-size: 12px;">Clarity 团队</p>
    </div>
  </body>
</html>
    """, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=True,
        )
        logger.info(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False
