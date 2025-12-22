import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics_event import AnalyticsEvent

logger = logging.getLogger(__name__)


class AnalyticsService:
    """分析事件服务 - 非关键路径，失败不影响主业务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def emit(
        self,
        event_type: str,
        session_id: Optional[UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Optional[AnalyticsEvent]:
        """记录分析事件，失败时仅记录日志不影响主流程"""
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                session_id=session_id,
                payload=payload,
            )
            self.db.add(event)
            await self.db.flush()
            return event
        except Exception as e:
            # 埋点失败不应影响主业务，仅记录日志
            logger.warning(
                f"Failed to emit analytics event: {event_type}, error: {e}"
            )
            return None
