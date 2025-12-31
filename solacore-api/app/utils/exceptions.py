from typing import Optional


class AuthError(Exception):
    def __init__(self, code: str, detail: Optional[str] = None, status_code: int = 400):
        self.code = code
        self.detail = detail or code
        self.status_code = status_code
        super().__init__(self.detail)


# 错误码到 HTTP 状态码的映射表
# 结构: (context, error_code) -> status_code
# 特殊规则用函数处理（如包含判断、code 转换）
_ERROR_STATUS_MAP: dict[tuple[str, str], int] = {
    # 注册相关
    ("register", "EMAIL_ALREADY_EXISTS"): 409,
    # 登录相关
    ("login", "INVALID_CREDENTIALS"): 401,
    ("login", "DEVICE_LIMIT_REACHED"): 403,
    ("login", "DEVICE_BOUND_TO_OTHER"): 403,
    ("beta_login", "INVALID_CREDENTIALS"): 401,
    ("beta_login", "DEVICE_LIMIT_REACHED"): 403,
    ("beta_login", "DEVICE_BOUND_TO_OTHER"): 403,
    # Token 刷新相关
    ("refresh", "INVALID_TOKEN"): 401,
    ("refresh", "TOKEN_EXPIRED"): 401,
    # 设备限制（通用）
    ("google_oauth_code", "DEVICE_LIMIT_REACHED"): 403,
    ("google_oauth_code", "DEVICE_BOUND_TO_OTHER"): 403,
    ("google_oauth", "DEVICE_LIMIT_REACHED"): 403,
    ("google_oauth", "DEVICE_BOUND_TO_OTHER"): 403,
    ("apple_oauth", "DEVICE_LIMIT_REACHED"): 403,
    ("apple_oauth", "DEVICE_BOUND_TO_OTHER"): 403,
}


def _get_oauth_error_config(
    context: str, error_code: str
) -> tuple[int, str, str] | None:
    """处理 OAuth 特殊错误（包含判断、code 转换）"""
    if context == "google_oauth_code" and "GOOGLE_" in error_code:
        return (401, error_code, error_code)
    if context == "google_oauth" and "GOOGLE_TOKEN_INVALID" in error_code:
        return (401, "INVALID_TOKEN", "INVALID_TOKEN")
    if context == "apple_oauth" and "APPLE_TOKEN" in error_code:
        return (401, "INVALID_TOKEN", "INVALID_TOKEN")
    return None


def auth_error_from_code(error_code: str, *, context: str) -> AuthError:
    """根据错误码和上下文生成 AuthError，使用映射表降低复杂度"""
    # 默认值
    code = error_code
    detail = error_code
    status_code = 400

    # 优先检查 OAuth 特殊规则（包含判断、code 转换）
    oauth_config = _get_oauth_error_config(context, error_code)
    if oauth_config:
        status_code, code, detail = oauth_config
    else:
        # 查询映射表
        status_code = _ERROR_STATUS_MAP.get((context, error_code), 400)

    return AuthError(code=code, detail=detail, status_code=status_code)


def raise_auth_error(error: ValueError, *, context: str) -> None:
    raise auth_error_from_code(str(error), context=context)
