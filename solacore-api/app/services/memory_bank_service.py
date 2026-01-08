from __future__ import annotations

import logging
from typing import Any, cast
from uuid import UUID

from app.models.solve_profile import SolveProfile
from app.schemas.orchestration import ProblemProfile
from app.utils.datetime_utils import utc_now
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class MemoryBankService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_or_create_profile(
        self, session_id: UUID, user_id: UUID
    ) -> SolveProfile:
        result = await self._db.execute(
            select(SolveProfile).where(SolveProfile.session_id == session_id)
        )
        row = result.scalar_one_or_none()
        if row:
            return row

        profile = ProblemProfile(session_id=session_id, user_id=user_id)
        entity = SolveProfile(
            session_id=session_id,
            schema_version=profile.meta.schema_version.value,
            profile=profile.model_dump(mode="json"),
        )

        async with self._db.begin_nested():
            self._db.add(entity)
            try:
                await self._db.flush()
                return entity
            except IntegrityError as e:
                logger.warning(
                    "Profile creation conflict for session_id=%s, user_id=%s: %s",
                    session_id,
                    user_id,
                    str(e.orig) if hasattr(e, "orig") else str(e),
                )

        result = await self._db.execute(
            select(SolveProfile).where(SolveProfile.session_id == session_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        raise ValueError("PROFILE_CREATE_CONFLICT")

    def load_profile(self, entity: SolveProfile) -> ProblemProfile:
        """加载 profile，遇到 schema 校验失败时降级处理"""
        data = cast(dict[str, Any], getattr(entity, "profile"))
        try:
            return ProblemProfile.model_validate(data)
        except ValidationError as e:
            logger.warning(
                "Profile schema validation failed for session %s (schema_version=%s), "
                "falling back to default profile. Error: %s",
                entity.session_id,
                entity.schema_version,
                str(e),
            )
            # 降级：返回默认 profile（保留 session_id 和 user_id）
            session_id = data.get("session_id", entity.session_id)
            user_id = data.get("user_id")
            return ProblemProfile(session_id=session_id, user_id=user_id)

    async def save_profile(self, entity: SolveProfile, profile: ProblemProfile) -> None:
        setattr(entity, "profile", profile.model_dump(mode="json"))
        setattr(entity, "schema_version", profile.meta.schema_version.value)
        setattr(entity, "updated_at", utc_now())
        self._db.add(entity)
        await self._db.flush()
