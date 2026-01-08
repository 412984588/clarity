from typing import Any, Dict, Union

COMMON_ERROR_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"error": "INVALID_TOKEN"}},
        },
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {"example": {"error": "FORBIDDEN"}},
        },
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {"example": {"error": "NOT_FOUND"}},
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"error": "INTERNAL_SERVER_ERROR"}},
        },
    },
}
