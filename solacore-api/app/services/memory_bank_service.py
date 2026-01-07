from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from app.models.solve_profile import SolveProfile
from app.schemas.orchestration import ProblemProfile
from app.utils.datetime_utils import utc_now
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
        self._db.add(entity)
        await self._db.flush()
        return entity

    def load_profile(self, entity: SolveProfile) -> ProblemProfile:
        data = cast(dict[str, Any], getattr(entity, "profile"))
        return ProblemProfile.model_validate(data)

    async def save_profile(self, entity: SolveProfile, profile: ProblemProfile) -> None:
        setattr(entity, "profile", profile.model_dump(mode="json"))
        setattr(entity, "schema_version", profile.meta.schema_version.value)
        setattr(entity, "updated_at", utc_now())
        self._db.add(entity)
        await self._db.flush()
