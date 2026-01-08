from __future__ import annotations

import re
from datetime import datetime

from app.schemas.orchestration import (
    AgentName,
    AgentRun,
    AuditFlag,
    AuditorOutput,
    ClarifyOutput,
    EmotionSnapshot,
    EmpathOutput,
    Hypothesis,
    HypothesisType,
    InfoGap,
    OptionItem,
    ProblemProfile,
    QuestionPlan,
    VisionaryOutput,
)
from app.services.content_filter import (
    looks_like_prompt_injection,
    sanitize_user_input,
    strip_pii,
)
from app.services.crisis_detector import detect_crisis
from app.services.emotion_detector import detect_emotion


def run_auditor(
    user_input: str,
    prompt_injection_policy: str = "warn",
    sanitized_input: str | None = None,
) -> AuditorOutput:
    crisis = detect_crisis(user_input)
    sanitized = (
        sanitized_input
        if sanitized_input is not None
        else strip_pii(sanitize_user_input(user_input))
    )
    flags: list[AuditFlag] = []

    if crisis.blocked:
        flags.append(AuditFlag.CRISIS)
        return AuditorOutput(
            allowed=False,
            sanitized_user_input=sanitized,
            flags=flags,
            reason="CRISIS",
        )

    if looks_like_prompt_injection(user_input):
        flags.append(AuditFlag.PROMPT_INJECTION)
        if prompt_injection_policy == "block":
            return AuditorOutput(
                allowed=False,
                sanitized_user_input=sanitized,
                flags=flags,
                reason="PROMPT_INJECTION",
            )

    if _looks_like_email(user_input):
        flags.append(AuditFlag.PII_EMAIL)
    if _looks_like_phone(user_input):
        flags.append(AuditFlag.PII_PHONE)

    return AuditorOutput(allowed=True, sanitized_user_input=sanitized, flags=flags)


def run_empath(user_input: str) -> EmpathOutput:
    emotion = detect_emotion(user_input)
    snapshot = EmotionSnapshot(
        label=emotion.emotion.value,
        confidence=emotion.confidence,
        intensity_1_5=_coarse_intensity(emotion.confidence),
    )

    core = _summarize_core_concern(user_input)
    message = _empath_message(core, snapshot.label)

    return EmpathOutput(
        emotion=snapshot,
        core_concern_summary=core,
        user_facing_message=message,
    )


def run_clarify(profile: ProblemProfile, user_input: str) -> ClarifyOutput:
    profile = _apply_user_input_to_profile(profile, user_input)
    info_gaps = _compute_info_gaps(profile)
    hypotheses = _compute_hypotheses(profile)

    next_question = _select_next_question(profile, info_gaps, hypotheses)
    user_facing = _clarify_message(profile, next_question)

    return ClarifyOutput(
        hypotheses=hypotheses,
        info_gaps=info_gaps,
        next_question=next_question,
        user_facing_message=user_facing,
    )


def run_visionary(profile: ProblemProfile, now_step: str) -> VisionaryOutput:
    goal = profile.user_goal or "把问题说清楚，并找到下一步"
    core = profile.core_concern_summary or "当前困扰"

    reframed = None
    if now_step == "reframe":
        reframed = f"如何在不牺牲{_first_constraint(profile)}的前提下，逐步实现：{goal}（围绕：{core}）？"

    options: list[OptionItem] = []
    if now_step in {"reframe", "options"}:
        options = [
            OptionItem(
                title="先把问题切成可控部分",
                description="列出你能控制的 3 件事和你无法控制的 3 件事，然后只对前者做动作。",
                pros=["立刻降低混乱感", "可快速启动"],
                cons=["需要接受部分不可控"],
            ),
            OptionItem(
                title="用最小实验验证一个关键假设",
                description="选一个最可能的原因，用一个 15 分钟内能完成的小实验来验证它。",
                pros=["信息增益高", "避免无效努力"],
                cons=["需要明确一个假设"],
            ),
            OptionItem(
                title="把目标改写成可衡量的 7 天版本",
                description="把目标拆成 7 天内可观察的指标，并设定每天 1 个最小动作。",
                pros=["更容易坚持", "更容易复盘"],
                cons=["需要一点规划时间"],
            ),
        ]

    response = "\n".join(
        [
            f"我试着把你的问题重新写成一个更可解的版本：{reframed}"
            if reframed
            else "我给你几个可能的方向：",
            "1) 先把问题切成可控部分：列出可控/不可控，各做 1 个动作",
            "2) 用最小实验验证一个关键假设：15 分钟内完成",
            "3) 把目标改写成 7 天可衡量版本：每天 1 个最小动作",
        ]
    )

    return VisionaryOutput(
        reframed_problem=reframed,
        options=options,
        user_facing_message=response,
    )


def append_run(
    profile: ProblemProfile, agent: AgentName, started_at: datetime, latency_ms: int
) -> None:
    profile.agent_runs.append(
        AgentRun(agent=agent, started_at=started_at, latency_ms=latency_ms)
    )


def _compute_info_gaps(profile: ProblemProfile) -> list[InfoGap]:
    gaps: list[InfoGap] = []

    if not profile.user_goal:
        gaps.append(
            InfoGap(
                key="user_goal",
                missing=True,
                importance=0.9,
                urgency=0.6,
                answerability=0.8,
                estimated_cost=0.2,
            )
        )

    if not profile.success_criteria:
        gaps.append(
            InfoGap(
                key="success_criteria",
                missing=True,
                importance=0.8,
                urgency=0.6,
                answerability=0.7,
                estimated_cost=0.2,
            )
        )

    if not profile.constraints:
        gaps.append(
            InfoGap(
                key="constraints",
                missing=True,
                importance=0.6,
                urgency=0.5,
                answerability=0.8,
                estimated_cost=0.2,
            )
        )

    if not profile.attempts:
        gaps.append(
            InfoGap(
                key="attempts",
                missing=True,
                importance=0.5,
                urgency=0.4,
                answerability=0.8,
                estimated_cost=0.2,
            )
        )

    return gaps


def _compute_hypotheses(profile: ProblemProfile) -> list[Hypothesis]:
    core = profile.core_concern_summary or ""
    base = [
        Hypothesis(
            id="H1",
            statement="目标/成功标准还不够清晰，导致行动难以落地",
            type=HypothesisType.GOAL_MISMATCH,
            confidence=0.34,
            tests_needed=["user_goal", "success_criteria"],
        ),
        Hypothesis(
            id="H2",
            statement="存在硬约束（时间/权限/资源）主导了局面",
            type=HypothesisType.CONSTRAINT,
            confidence=0.33,
            tests_needed=["constraints"],
        ),
        Hypothesis(
            id="H3",
            statement="情绪负荷过高影响了专注与决策",
            type=HypothesisType.EMOTIONAL_BLOCK,
            confidence=0.33,
            tests_needed=["emotion"],
        ),
    ]

    if profile.emotion and profile.emotion.label in {"anxious", "sad", "confused"}:
        base[2].confidence = min(0.6, base[2].confidence + 0.15)

    if core and any(
        word in core for word in ["deadline", "交付", "下周", "明天", "月底"]
    ):
        base[1].confidence = min(0.6, base[1].confidence + 0.15)

    return base


def _select_next_question(
    profile: ProblemProfile, gaps: list[InfoGap], hypotheses: list[Hypothesis]
) -> QuestionPlan:
    missing_keys = {gap.key for gap in gaps if gap.missing}

    if profile.meta.clarify_state == "INIT":
        profile.meta.clarify_state = "ALIGN"

    if profile.meta.clarify_turn_index >= 5:
        profile.meta.clarify_state = "DONE"
        return QuestionPlan(
            prompt="如果只能选一个‘今天 10 分钟内能做的最小动作’，你愿意先做哪个？",
            rationale="在信息不完整时先推动一个最小可执行动作",
            expected_fields=[],
            allow_unknown=True,
        )

    if "user_goal" in missing_keys or "success_criteria" in missing_keys:
        profile.meta.clarify_state = "ALIGN"
        return QuestionPlan(
            prompt="你希望这件事最终变成什么样才算‘解决了’？如果有 1-2 个可量化的标准，也可以顺便说一下",
            rationale="先对齐成功标准，避免解决错问题",
            expected_fields=["user_goal", "success_criteria"],
            allow_unknown=True,
        )

    if "constraints" in missing_keys:
        profile.meta.clarify_state = "MAP"
        return QuestionPlan(
            prompt="这件事现在最大的硬约束是什么？比如时间点、资源、权限、必须交付的范围（选 1-2 个最关键的）",
            rationale="把约束说清楚，才能评估可行路径",
            expected_fields=["constraints"],
            allow_unknown=True,
        )

    if "attempts" in missing_keys:
        profile.meta.clarify_state = "MAP"
        return QuestionPlan(
            prompt="你已经尝试过哪些办法？分别带来了什么结果（哪怕很小也行）",
            rationale="避免重复无效尝试，并找到可复用的有效点",
            expected_fields=["attempts"],
            allow_unknown=True,
        )

    profile.meta.clarify_state = "DIAGNOSE"
    top = sorted(hypotheses, key=lambda h: h.confidence, reverse=True)[:2]
    focus = " / ".join(h.statement for h in top)

    return QuestionPlan(
        prompt=f"在下面两种可能里，你更像哪一种？A) {top[0].statement}  B) {top[1].statement}（也可以说都不是）",
        rationale=f"用一个低负担问题区分最可能的两条路径（当前关注：{focus}）",
        expected_fields=[],
        allow_unknown=True,
    )


def _apply_user_input_to_profile(
    profile: ProblemProfile, user_input: str
) -> ProblemProfile:
    if profile.core_concern_summary is None:
        profile.core_concern_summary = _summarize_core_concern(user_input)

    if profile.meta.clarify_state in {"ALIGN", "INIT"} and profile.user_goal is None:
        extracted_goal = _extract_goal(user_input)
        if extracted_goal:
            profile.user_goal = extracted_goal

        extracted_criteria = _extract_success_criteria(user_input)
        if extracted_criteria and not profile.success_criteria:
            profile.success_criteria = extracted_criteria

    if profile.meta.clarify_state == "MAP":
        constraints = _extract_constraints(user_input)
        if constraints:
            profile.constraints.extend(constraints)
        attempts = _extract_attempts(user_input)
        if attempts:
            profile.attempts.extend(attempts)

    if profile.meta.clarify_turn_index < 10:
        profile.meta.clarify_turn_index += 1

    return profile


def _clarify_message(profile: ProblemProfile, question: QuestionPlan) -> str:
    prefix = "我们先把最关键的信息补齐一下，这样后面给的建议才不会跑偏"
    if profile.emotion and profile.emotion.label in {"anxious", "sad"}:
        prefix = "我能理解你现在的压力/难受。我们先把最关键的信息补齐一下，好吗"

    return f"{prefix}\n\n{question.prompt}"


def _empath_message(core: str, emotion_label: str) -> str:
    tone = {
        "anxious": "听起来你有点紧绷和担心",
        "sad": "听起来这让你挺难过",
        "confused": "我能感受到你有点困惑",
    }.get(emotion_label, "我听到你现在有不少压力")

    return f"{tone}。我理解你在面对：{core}。我们可以一步一步来。"


def _summarize_core_concern(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= 60:
        return cleaned
    return cleaned[:57] + "..."


def _extract_goal(text: str) -> str | None:
    cleaned = text.strip()
    if not cleaned:
        return None
    if len(cleaned) > 120:
        return None
    return cleaned


def _extract_success_criteria(text: str) -> list[str] | None:
    if not text.strip():
        return None
    parts = re.split(r"[\n。；;]+", text)
    items = [p.strip() for p in parts if p.strip()]
    if not items:
        return None
    if len(items) > 5:
        items = items[:5]
    return items


def _extract_constraints(text: str) -> list[str]:
    items = []
    for token in re.split(r"[\n，,。；;]+", text):
        token = token.strip()
        if not token:
            continue
        if len(token) > 60:
            continue
        items.append(token)
    return items[:5]


def _extract_attempts(text: str) -> list[str]:
    items = []
    for token in re.split(r"[\n，,。；;]+", text):
        token = token.strip()
        if not token:
            continue
        if len(token) > 60:
            continue
        items.append(token)
    return items[:5]


def _first_constraint(profile: ProblemProfile) -> str:
    if profile.constraints:
        return profile.constraints[0]
    return "现有约束"


def _looks_like_email(text: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))


def _looks_like_phone(text: str) -> bool:
    return bool(re.search(r"\+?\d[\d\s().-]{8,}\d", text))


def _coarse_intensity(confidence: float) -> int:
    if confidence >= 0.85:
        return 4
    if confidence >= 0.65:
        return 3
    return 2
