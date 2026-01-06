"""邮件服务单元测试"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.email_service import send_password_reset_email


@pytest.mark.asyncio
async def test_send_password_reset_email_smtp_disabled(monkeypatch: pytest.MonkeyPatch):
    """测试 SMTP 禁用时不发送邮件"""
    # Mock settings
    fake_settings = MagicMock()
    fake_settings.smtp_enabled = False
    monkeypatch.setattr("app.services.email_service.settings", fake_settings)

    result = await send_password_reset_email("user@example.com", "test-token-123")

    assert result is False


@pytest.mark.asyncio
async def test_send_password_reset_email_success(monkeypatch: pytest.MonkeyPatch):
    """测试邮件发送成功"""
    # Mock settings
    fake_settings = MagicMock()
    fake_settings.smtp_enabled = True
    fake_settings.frontend_url = "https://example.com"
    fake_settings.smtp_from_name = "Solacore"
    fake_settings.smtp_from = "noreply@solacore.com"
    fake_settings.smtp_host = "smtp.gmail.com"
    fake_settings.smtp_port = 587
    fake_settings.smtp_user = "test@solacore.com"
    fake_settings.smtp_password = "test-password"
    monkeypatch.setattr("app.services.email_service.settings", fake_settings)

    # Mock aiosmtplib.send
    mock_send = AsyncMock()
    monkeypatch.setattr("app.services.email_service.aiosmtplib.send", mock_send)

    result = await send_password_reset_email("user@example.com", "test-token-123")

    assert result is True
    mock_send.assert_called_once()

    # 验证邮件内容
    call_args = mock_send.call_args
    message = call_args[0][0]
    assert message["From"] == "Solacore <noreply@solacore.com>"
    assert message["To"] == "user@example.com"
    assert message["Subject"] == "密码重置 - Solacore"

    # 验证邮件正文包含重置链接（multipart/alternative 需要遍历部分）
    text_parts = [
        part for part in message.walk() if part.get_content_type() == "text/plain"
    ]
    assert len(text_parts) > 0
    body = text_parts[0].get_content()
    assert "https://example.com/auth/reset?token=test-token-123" in body

    # 验证 SMTP 参数
    assert call_args[1]["hostname"] == "smtp.gmail.com"
    assert call_args[1]["port"] == 587
    assert call_args[1]["username"] == "test@solacore.com"
    assert call_args[1]["password"] == "test-password"
    assert call_args[1]["start_tls"] is True  # 端口 587 使用 STARTTLS


@pytest.mark.asyncio
async def test_send_password_reset_email_smtp_failure(monkeypatch: pytest.MonkeyPatch):
    """测试 SMTP 发送失败时返回 False"""
    # Mock settings
    fake_settings = MagicMock()
    fake_settings.smtp_enabled = True
    fake_settings.frontend_url = "https://example.com"
    fake_settings.smtp_from_name = "Solacore"
    fake_settings.smtp_from = "noreply@solacore.com"
    fake_settings.smtp_host = "smtp.gmail.com"
    fake_settings.smtp_port = 587
    fake_settings.smtp_user = "test@solacore.com"
    fake_settings.smtp_password = "test-password"
    monkeypatch.setattr("app.services.email_service.settings", fake_settings)

    # Mock aiosmtplib.send to raise exception
    mock_send = AsyncMock(side_effect=Exception("SMTP connection failed"))
    monkeypatch.setattr("app.services.email_service.aiosmtplib.send", mock_send)

    result = await send_password_reset_email("user@example.com", "test-token-123")

    assert result is False
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_password_reset_email_html_alternative(
    monkeypatch: pytest.MonkeyPatch,
):
    """测试邮件包含 HTML 版本"""
    # Mock settings
    fake_settings = MagicMock()
    fake_settings.smtp_enabled = True
    fake_settings.frontend_url = "https://example.com"
    fake_settings.smtp_from_name = "Solacore"
    fake_settings.smtp_from = "noreply@solacore.com"
    fake_settings.smtp_host = "smtp.gmail.com"
    fake_settings.smtp_port = 587
    fake_settings.smtp_user = "test@solacore.com"
    fake_settings.smtp_password = "test-password"
    monkeypatch.setattr("app.services.email_service.settings", fake_settings)

    # Mock aiosmtplib.send
    mock_send = AsyncMock()
    monkeypatch.setattr("app.services.email_service.aiosmtplib.send", mock_send)

    await send_password_reset_email("user@example.com", "test-token-123")

    # 验证邮件包含 HTML 版本
    message = mock_send.call_args[0][0]
    html_parts = [
        part for part in message.walk() if part.get_content_type() == "text/html"
    ]

    assert len(html_parts) > 0
    html_content = html_parts[0].get_content()
    assert (
        '<a href="https://example.com/auth/reset?token=test-token-123"' in html_content
    )
    assert "重置密码" in html_content


@pytest.mark.asyncio
async def test_send_password_reset_email_token_in_link(
    monkeypatch: pytest.MonkeyPatch,
):
    """测试邮件链接包含正确的 token"""
    # Mock settings
    fake_settings = MagicMock()
    fake_settings.smtp_enabled = True
    fake_settings.frontend_url = "https://app.solacore.com"
    fake_settings.smtp_from_name = "Solacore"
    fake_settings.smtp_from = "noreply@solacore.com"
    fake_settings.smtp_host = "smtp.gmail.com"
    fake_settings.smtp_port = 587
    fake_settings.smtp_user = "test@solacore.com"
    fake_settings.smtp_password = "test-password"
    monkeypatch.setattr("app.services.email_service.settings", fake_settings)

    # Mock aiosmtplib.send
    mock_send = AsyncMock()
    monkeypatch.setattr("app.services.email_service.aiosmtplib.send", mock_send)

    custom_token = "abc123xyz789"
    await send_password_reset_email("user@example.com", custom_token)

    # 验证邮件内容包含自定义 token（multipart/alternative 需要遍历部分）
    message = mock_send.call_args[0][0]
    text_parts = [
        part for part in message.walk() if part.get_content_type() == "text/plain"
    ]
    assert len(text_parts) > 0
    body = text_parts[0].get_content()
    assert f"https://app.solacore.com/auth/reset?token={custom_token}" in body
