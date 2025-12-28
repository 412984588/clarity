from typing import Optional


class AuthError(Exception):
    def __init__(self, code: str, detail: Optional[str] = None, status_code: int = 400):
        self.code = code
        self.detail = detail or code
        self.status_code = status_code
        super().__init__(self.detail)


def auth_error_from_code(error_code: str, *, context: str) -> AuthError:
    code = error_code
    detail = error_code
    status_code = 400

    if context == "register":
        if error_code == "EMAIL_ALREADY_EXISTS":
            status_code = 409
    elif context in {"login", "beta_login"}:
        if error_code == "INVALID_CREDENTIALS":
            status_code = 401
        elif error_code in {"DEVICE_LIMIT_REACHED", "DEVICE_BOUND_TO_OTHER"}:
            status_code = 403
    elif context == "refresh":
        if error_code in {"INVALID_TOKEN", "TOKEN_EXPIRED"}:
            status_code = 401
    elif context == "google_oauth_code":
        if "GOOGLE_" in error_code:
            status_code = 401
        elif error_code in {"DEVICE_LIMIT_REACHED", "DEVICE_BOUND_TO_OTHER"}:
            status_code = 403
    elif context == "google_oauth":
        if "GOOGLE_TOKEN_INVALID" in error_code:
            status_code = 401
            code = "INVALID_TOKEN"
            detail = "INVALID_TOKEN"
        elif error_code in {"DEVICE_LIMIT_REACHED", "DEVICE_BOUND_TO_OTHER"}:
            status_code = 403
    elif context == "apple_oauth":
        if "APPLE_TOKEN" in error_code:
            status_code = 401
            code = "INVALID_TOKEN"
            detail = "INVALID_TOKEN"
        elif error_code in {"DEVICE_LIMIT_REACHED", "DEVICE_BOUND_TO_OTHER"}:
            status_code = 403

    return AuthError(code=code, detail=detail, status_code=status_code)


def raise_auth_error(error: ValueError, *, context: str) -> None:
    raise auth_error_from_code(str(error), context=context)
