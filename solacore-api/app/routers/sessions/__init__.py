# 会话路由聚合模块：整合子路由并导出主要端点

from fastapi import APIRouter

from .create import create_session
from .create import router as create_router
from .delete import delete_session
from .delete import router as delete_router
from .list import get_session, list_sessions
from .list import router as list_router
from .stream import router as stream_router
from .stream import stream_messages
from .update import router as update_router
from .update import update_session

router = APIRouter(prefix="/sessions", tags=["Sessions"])
router.include_router(create_router)
router.include_router(list_router)
router.include_router(stream_router)
router.include_router(update_router)
router.include_router(delete_router)

__all__ = [
    "router",
    "create_session",
    "list_sessions",
    "get_session",
    "stream_messages",
    "update_session",
    "delete_session",
]
