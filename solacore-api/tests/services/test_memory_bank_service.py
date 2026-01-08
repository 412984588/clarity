"""
MemoryBankService 单元测试

覆盖函数：
- get_or_create_profile: 获取或创建 profile（含并发场景）
- load_profile: 加载 profile
- save_profile: 保存 profile
"""

import asyncio
from uuid import uuid4

import pytest
from app.models.solve_profile import SolveProfile
from app.models.solve_session import SolveSession, SolveStep
from app.models.user import User
from app.schemas.orchestration import ProblemProfile
from app.services.memory_bank_service import MemoryBankService
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
class TestGetOrCreateProfile:
    async def test_create_new_profile(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            service = MemoryBankService(db)
            profile = await service.get_or_create_profile(session.id, user.id)

            assert profile is not None
            assert profile.session_id == session.id
            assert profile.schema_version == "v1"

            loaded = service.load_profile(profile)
            assert loaded.session_id == session.id
            assert loaded.user_id == user.id

    async def test_get_existing_profile(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            service = MemoryBankService(db)
            profile1 = await service.get_or_create_profile(session.id, user.id)
            profile2 = await service.get_or_create_profile(session.id, user.id)

            assert profile1.id == profile2.id

    async def test_concurrent_create_same_profile(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.commit()

            session_id = session.id
            user_id = user.id

            async def create_profile():
                async with TestingSessionLocal() as new_db:
                    service = MemoryBankService(new_db)
                    profile = await service.get_or_create_profile(session_id, user_id)
                    await new_db.commit()
                    return profile

            results = await asyncio.gather(
                create_profile(),
                create_profile(),
                create_profile(),
                return_exceptions=True,
            )

            successful_profiles = [r for r in results if isinstance(r, SolveProfile)]
            assert len(successful_profiles) == 3

            profile_ids = {p.id for p in successful_profiles}
            assert len(profile_ids) == 1

            async with TestingSessionLocal() as verify_db:
                result = await verify_db.execute(
                    select(SolveProfile).where(SolveProfile.session_id == session_id)
                )
                all_profiles = result.scalars().all()
                assert len(all_profiles) == 1


@pytest.mark.asyncio
class TestLoadProfile:
    async def test_load_profile_success(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            service = MemoryBankService(db)
            profile_entity = await service.get_or_create_profile(session.id, user.id)

            loaded = service.load_profile(profile_entity)

            assert isinstance(loaded, ProblemProfile)
            assert loaded.session_id == session.id
            assert loaded.user_id == user.id
            assert loaded.meta.schema_version.value == "v1"

    async def test_load_profile_corrupted_data_fallback(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            session_id_val = session.id
            user_id_val = user.id

            corrupted_entity = SolveProfile(
                session_id=session_id_val,
                schema_version="v1",
                profile={
                    "session_id": str(session_id_val),
                    "user_id": str(user_id_val),
                    "meta": {"invalid_field": "bad_value"},
                },
            )
            db.add(corrupted_entity)
            await db.flush()

            service = MemoryBankService(db)
            loaded = service.load_profile(corrupted_entity)

            assert isinstance(loaded, ProblemProfile)
            assert loaded.session_id == session_id_val
            assert loaded.user_id == user_id_val
            assert loaded.meta.schema_version.value == "v1"


@pytest.mark.asyncio
class TestSaveProfile:
    async def test_save_profile_updates_fields(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            service = MemoryBankService(db)
            profile_entity = await service.get_or_create_profile(session.id, user.id)
            profile = service.load_profile(profile_entity)

            profile.core_concern_summary = "测试问题"
            profile.constraints.append("约束1")

            await service.save_profile(profile_entity, profile)
            await db.commit()

            result = await db.execute(
                select(SolveProfile).where(SolveProfile.id == profile_entity.id)
            )
            saved = result.scalar_one()
            reloaded = service.load_profile(saved)

            assert reloaded.core_concern_summary == "测试问题"
            assert "约束1" in reloaded.constraints
