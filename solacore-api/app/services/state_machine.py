from typing import Dict, Tuple

from app.models.solve_session import SolveStep

VALID_TRANSITIONS: Dict[SolveStep, Tuple[SolveStep, ...]] = {
    SolveStep.RECEIVE: (SolveStep.CLARIFY,),
    SolveStep.CLARIFY: (SolveStep.REFRAME,),
    SolveStep.REFRAME: (SolveStep.OPTIONS,),
    SolveStep.OPTIONS: (SolveStep.COMMIT,),
    SolveStep.COMMIT: (),
}


def validate_transition(current: SolveStep, next_step: SolveStep) -> bool:
    """验证状态转换是否合法"""
    return next_step in VALID_TRANSITIONS.get(current, ())


def can_transition(current: SolveStep, next_step: SolveStep) -> bool:
    """检查状态转换是否合法"""
    return validate_transition(current, next_step)


def get_next_step(current: SolveStep) -> SolveStep | None:
    """获取下一步，如果是终态返回 None"""
    next_steps = {
        SolveStep.RECEIVE: SolveStep.CLARIFY,
        SolveStep.CLARIFY: SolveStep.REFRAME,
        SolveStep.REFRAME: SolveStep.OPTIONS,
        SolveStep.OPTIONS: SolveStep.COMMIT,
    }
    return next_steps.get(current)


def is_final_step(step: SolveStep) -> bool:
    """检查是否为终态"""
    return not VALID_TRANSITIONS.get(step)
