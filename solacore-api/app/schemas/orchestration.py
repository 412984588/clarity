from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from app.schemas.fields import Field
from app.utils.datetime_utils import utc_now
from pydantic import BaseModel, ConfigDict


class AgentName(str, Enum):
    EMPATH = "empath"
    CLARIFY = "clarify"
    VISIONARY = "visionary"
    AUDITOR = "auditor"


class OrchestrationMode(str, Enum):
    SOLVE = "solve"
    LEARN = "learn"


class ProfileSchemaVersion(str, Enum):
    V1 = "v1"


class ProblemDomain(str, Enum):
    WORK = "work"
    CAREER = "career"
    RELATIONSHIP = "relationship"
    HEALTH = "health"
    FINANCE = "finance"
    TECH = "tech"
    OTHER = "other"


class ProfileMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: ProfileSchemaVersion = Field(
        default=ProfileSchemaVersion.V1,
        description="ProblemProfile schema 版本",
        examples=["v1"],
    )
    mode: OrchestrationMode = Field(
        default=OrchestrationMode.SOLVE,
        description="Profile 模式（Solve/Learn）",
        examples=["solve"],
    )
    last_updated_at: datetime = Field(
        default_factory=lambda: utc_now(),
        description="最近更新时间（UTC）",
    )
    clarify_state: Literal["INIT", "ALIGN", "MAP", "DIAGNOSE", "COMMIT", "DONE"] = (
        Field(
            default="INIT",
            description="Clarify 内部状态（<=5 轮）",
            examples=["MAP"],
        )
    )
    clarify_turn_index: int = Field(
        default=0,
        description="Clarify 已提问轮次",
        examples=[0, 1, 2],
        ge=0,
    )


class EmotionSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="情绪标签", examples=["sad"])
    confidence: float = Field(
        ..., description="情绪置信度（0-1）", examples=[0.8], ge=0.0, le=1.0
    )
    intensity_1_5: int = Field(
        default=3,
        description="情绪强度（1-5）",
        examples=[3, 4],
        ge=1,
        le=5,
    )


class HypothesisType(str, Enum):
    ROOT_CAUSE = "root_cause"
    CONSTRAINT = "constraint"
    GOAL_MISMATCH = "goal_mismatch"
    SKILL_GAP = "skill_gap"
    PROCESS_GAP = "process_gap"
    EMOTIONAL_BLOCK = "emotional_block"


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="假设 ID", examples=["H1"])
    statement: str = Field(..., description="可检验的假设陈述")
    type: HypothesisType = Field(..., description="假设类型")
    confidence: float = Field(
        default=0.33,
        description="置信度（0-1）",
        examples=[0.2, 0.6],
        ge=0.0,
        le=1.0,
    )
    tests_needed: list[str] = Field(
        default_factory=list,
        description="验证该假设还缺哪些字段",
        examples=[["constraints.deadlines", "current_state.when"]],
    )


class InfoGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(
        ..., description="缺口字段 key", examples=["goal.success_criteria"]
    )
    missing: bool = Field(..., description="是否缺失")
    importance: float = Field(
        default=0.5,
        description="重要性（0-1）",
        examples=[0.9],
        ge=0.0,
        le=1.0,
    )
    urgency: float = Field(
        default=0.5,
        description="紧急性（0-1）",
        examples=[0.7],
        ge=0.0,
        le=1.0,
    )
    answerability: float = Field(
        default=0.7,
        description="可回答性（0-1）",
        examples=[0.8],
        ge=0.0,
        le=1.0,
    )
    estimated_cost: float = Field(
        default=0.2,
        description="回答成本（0-1）",
        examples=[0.1, 0.4],
        ge=0.0,
        le=1.0,
    )


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: AgentName = Field(..., description="Agent 名称")
    started_at: datetime = Field(default_factory=lambda: utc_now())
    latency_ms: int = Field(default=0, ge=0)
    token_usage: dict[str, int] | None = Field(default=None)
    notes: str | None = Field(default=None)


class ProblemProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID = Field(..., description="Solve/Learn 会话 ID")
    user_id: UUID | None = Field(default=None, description="用户 ID（可选）")

    meta: ProfileMeta = Field(default_factory=ProfileMeta)
    domain: ProblemDomain = Field(default=ProblemDomain.OTHER)

    core_concern_summary: str | None = Field(default=None)
    user_goal: str | None = Field(default=None)
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    attempts: list[str] = Field(default_factory=list)

    emotion: EmotionSnapshot | None = Field(default=None)

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    info_gaps: list[InfoGap] = Field(default_factory=list)
    last_questions: list[str] = Field(default_factory=list)

    agent_runs: list[AgentRun] = Field(default_factory=list)


class AuditFlag(str, Enum):
    CRISIS = "crisis"
    PROMPT_INJECTION = "prompt_injection"
    PII_EMAIL = "pii_email"
    PII_PHONE = "pii_phone"


class AuditorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool = Field(...)
    sanitized_user_input: str = Field(...)
    flags: list[AuditFlag] = Field(default_factory=list)
    reason: str | None = Field(default=None)


class EmpathOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emotion: EmotionSnapshot | None = Field(default=None)
    core_concern_summary: str = Field(...)
    user_facing_message: str = Field(...)


class QuestionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(...)
    rationale: str = Field(...)
    expected_fields: list[str] = Field(default_factory=list)
    allow_unknown: bool = Field(default=True)


class ClarifyOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    info_gaps: list[InfoGap] = Field(default_factory=list)
    next_question: QuestionPlan = Field(...)
    user_facing_message: str = Field(...)


class OptionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(...)
    description: str = Field(...)
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class VisionaryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reframed_problem: str | None = Field(default=None)
    options: list[OptionItem] = Field(default_factory=list)
    user_facing_message: str = Field(...)


class OrchestratorDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_agent: AgentName = Field(...)
    next_step: str = Field(...)
    response_text: str = Field(...)
    profile: ProblemProfile = Field(...)
    audit: AuditorOutput = Field(...)


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: ProblemProfile = Field(...)
    user_input: str = Field(...)
    now_step: str = Field(...)


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: AgentName = Field(...)
    output: dict[str, Any] = Field(...)
    user_facing_text: str | None = Field(default=None)
