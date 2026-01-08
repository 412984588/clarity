from __future__ import annotations

import time
from uuid import UUID

from app.config import get_settings
from app.models.solve_session import SolveSession, SolveStep
from app.schemas.orchestration import AgentName, OrchestratorDecision
from app.services.crisis_detector import get_crisis_response
from app.services.memory_bank_service import MemoryBankService
from app.services.orchestration_agents import (
    append_run,
    run_auditor,
    run_clarify,
    run_empath,
    run_visionary,
)
from app.utils.datetime_utils import utc_now
from sqlalchemy.ext.asyncio import AsyncSession


class OrchestratorService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._memory = MemoryBankService(db)
        self._settings = get_settings()

    async def handle_solve_message(
        self, session: SolveSession, user_input: str, current_step: SolveStep
    ) -> OrchestratorDecision:
        profile_entity = await self._memory.get_or_create_profile(
            session_id=UUID(str(session.id)),
            user_id=UUID(str(session.user_id)),
        )
        profile = self._memory.load_profile(profile_entity)

        audit_started = utc_now()
        audit0 = time.perf_counter()
        audit = run_auditor(user_input, self._settings.prompt_injection_policy)
        append_run(
            profile,
            AgentName.AUDITOR,
            audit_started,
            int((time.perf_counter() - audit0) * 1000),
        )

        if not audit.allowed:
            decision = OrchestratorDecision(
                primary_agent=AgentName.AUDITOR,
                next_step=current_step.value,
                response_text=get_crisis_response().get("message", ""),
                profile=profile,
                audit=audit,
            )
            await self._memory.save_profile(profile_entity, profile)
            return decision

        solve_step = current_step
        now_step = current_step.value

        response_text = ""
        next_step = now_step
        primary = AgentName.CLARIFY

        if solve_step == SolveStep.RECEIVE:
            primary = AgentName.EMPATH
            started = utc_now()
            t0 = time.perf_counter()
            empath = run_empath(audit.sanitized_user_input)
            append_run(
                profile,
                AgentName.EMPATH,
                started,
                int((time.perf_counter() - t0) * 1000),
            )

            profile.core_concern_summary = empath.core_concern_summary
            profile.emotion = empath.emotion
            response_text = empath.user_facing_message
            next_step = SolveStep.CLARIFY.value

        elif solve_step == SolveStep.CLARIFY:
            primary = AgentName.CLARIFY
            started = utc_now()
            t0 = time.perf_counter()
            clarify = run_clarify(profile, audit.sanitized_user_input)
            append_run(
                profile,
                AgentName.CLARIFY,
                started,
                int((time.perf_counter() - t0) * 1000),
            )

            profile.hypotheses = clarify.hypotheses
            profile.info_gaps = clarify.info_gaps
            profile.last_questions.append(clarify.next_question.prompt)
            response_text = clarify.user_facing_message

            done = profile.meta.clarify_state == "DONE" or (
                bool(profile.user_goal)
                and bool(profile.success_criteria)
                and bool(profile.constraints)
                and profile.meta.clarify_turn_index >= 2
            )
            next_step = SolveStep.REFRAME.value if done else SolveStep.CLARIFY.value

        elif solve_step in {SolveStep.REFRAME, SolveStep.OPTIONS}:
            primary = AgentName.VISIONARY
            started = utc_now()
            t0 = time.perf_counter()
            visionary = run_visionary(profile, now_step)
            append_run(
                profile,
                AgentName.VISIONARY,
                started,
                int((time.perf_counter() - t0) * 1000),
            )

            response_text = visionary.user_facing_message
            next_step = (
                SolveStep.OPTIONS.value
                if solve_step == SolveStep.REFRAME
                else SolveStep.COMMIT.value
            )

        else:
            primary = AgentName.CLARIFY
            response_text = "我们收个尾：如果只能选一个‘今天 10 分钟内能做的最小动作’，你愿意先做哪个？"
            next_step = SolveStep.COMMIT.value

        profile.meta.last_updated_at = utc_now()
        await self._memory.save_profile(profile_entity, profile)

        return OrchestratorDecision(
            primary_agent=primary,
            next_step=next_step,
            response_text=response_text,
            profile=profile,
            audit=audit,
        )
