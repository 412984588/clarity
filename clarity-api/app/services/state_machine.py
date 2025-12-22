from typing import Dict, Optional, Tuple

from app.models.solve_session import SolveStep


VALID_TRANSITIONS: Dict[SolveStep, Tuple[SolveStep, ...]] = {
    SolveStep.RECEIVE: (SolveStep.CLARIFY,),
    SolveStep.CLARIFY: (SolveStep.REFRAME,),
    SolveStep.REFRAME: (SolveStep.OPTIONS,),
    SolveStep.OPTIONS: (SolveStep.COMMIT,),
    SolveStep.COMMIT: (),
}


def can_transition(current: SolveStep, next_step: SolveStep) -> bool:
    """检查状态转换是否合法"""
    return next_step in VALID_TRANSITIONS.get(current, ())


def get_next_step(current: SolveStep) -> Optional[SolveStep]:
    """获取下一个状态（如果存在）"""
    next_steps = VALID_TRANSITIONS.get(current)
    if not next_steps:
        return None
    return next_steps[0]


def is_final_step(step: SolveStep) -> bool:
    """检查是否为终态"""
    return not VALID_TRANSITIONS.get(step)
