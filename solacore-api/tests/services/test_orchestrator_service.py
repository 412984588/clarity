"""
OrchestratorService 单元测试

覆盖函数：
- handle_solve_message: 处理 solve 消息并返回编排决策
- 状态机转换：RECEIVE -> CLARIFY -> REFRAME/OPTIONS -> COMMIT
"""

from uuid import uuid4

import pytest
from app.models.solve_session import SolveSession, SolveStep
from app.models.user import User
from app.services.orchestrator_service import OrchestratorService
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
class TestOrchestratorStateTransitions:
    async def test_receive_to_clarify_transition(self):
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

            orchestrator = OrchestratorService(db)
            decision = await orchestrator.handle_solve_message(
                session, "我想提升工作效率", SolveStep.RECEIVE
            )

            assert decision.primary_agent.value == "empath"
            assert decision.next_step == SolveStep.CLARIFY.value
            assert decision.response_text is not None
            assert len(decision.response_text) > 0

    async def test_clarify_stays_in_clarify_when_incomplete(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.CLARIFY.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            orchestrator = OrchestratorService(db)
            decision = await orchestrator.handle_solve_message(
                session, "我想提升效率", SolveStep.CLARIFY
            )

            assert decision.primary_agent.value == "clarify"
            assert decision.next_step == SolveStep.CLARIFY.value

    async def test_clarify_to_reframe_when_sufficient_info(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.CLARIFY.value,
                locale="zh-CN",
            )
            db.add(session)
            await db.flush()

            orchestrator = OrchestratorService(db)

            for _ in range(6):
                decision = await orchestrator.handle_solve_message(
                    session,
                    "我想在3个月内提升工作效率20%，主要约束是时间有限，已经尝试过番茄工作法但效果不佳",
                    SolveStep.CLARIFY,
                )

            assert decision.next_step in [
                SolveStep.REFRAME.value,
                SolveStep.OPTIONS.value,
            ]

    async def test_auditor_blocks_crisis_input(self):
        async with TestingSessionLocal() as db:
            user = User(email=f"test-{uuid4().hex}@example.com", password_hash="hash")
            db.add(user)
            await db.flush()

            session = SolveSession(
                user_id=user.id,
                current_step=SolveStep.RECEIVE.value,
                locale="en-US",
            )
            db.add(session)
            await db.flush()

            orchestrator = OrchestratorService(db)
            decision = await orchestrator.handle_solve_message(
                session, "I want to kill myself", SolveStep.RECEIVE
            )

            assert decision.primary_agent.value == "auditor"
            assert decision.audit.allowed is False
            assert decision.next_step == SolveStep.RECEIVE.value


@pytest.mark.asyncio
class TestOrchestratorProfilePersistence:
    async def test_profile_persists_across_messages(self):
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

            orchestrator = OrchestratorService(db)

            decision1 = await orchestrator.handle_solve_message(
                session, "我想提升工作效率", SolveStep.RECEIVE
            )

            decision2 = await orchestrator.handle_solve_message(
                session, "我的目标是3个月内提升20%", SolveStep.CLARIFY
            )

            assert decision1.profile.session_id == decision2.profile.session_id
            assert len(decision2.profile.agent_runs) > len(decision1.profile.agent_runs)
