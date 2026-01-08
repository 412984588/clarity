"""邮件服务"""

import logging
from email.message import EmailMessage

import aiosmtplib
from app.config import get_settings

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
    message["Subject"] = "密码重置 - Solacore"

    message.set_content(f"""
您好，

您请求重置 Solacore 账户的密码。请点击以下链接重置密码：

{reset_link}

此链接将在30分钟后过期。

如果您没有请求重置密码，请忽略此邮件。

Solacore 团队
    """)

    message.add_alternative(
        f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #4CAF50;">密码重置</h2>
      <p>您好，</p>
      <p>您请求重置 Solacore 账户的密码。</p>
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
      <p style="color: #999; font-size: 12px;">Solacore 团队</p>
    </div>
  </body>
</html>
    """,
        subtype="html",
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Password reset email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error(
            "Failed to send password reset email to %s: %s",
            to_email,
            str(e),
            exc_info=True,
            extra={"to_email": to_email, "smtp_host": settings.smtp_host},
        )
        return False
