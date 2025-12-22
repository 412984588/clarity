# Epic 5: Solve 5-Step - Task List

## Wave 1 Tasks

### Task 1: Database Migration

**目标**: 创建 step_history 和 analytics_events 表

**步骤**:
```bash
cd clarity-api

# 1. 创建 migration
alembic revision --autogenerate -m "add step_history and analytics_events"

# 2. 检查生成的 migration 文件
cat alembic/versions/*add_step_history*.py

# 3. 应用 migration
alembic upgrade head

# 4. 验证表存在
psql $DATABASE_URL -c "\dt step_history"
psql $DATABASE_URL -c "\dt analytics_events"
```

**验收**:
```bash
psql $DATABASE_URL -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'step_history';"
# 预期: id, session_id, step, started_at, completed_at, message_count
```

---

### Task 2: StepHistory Model

**目标**: 创建 `app/models/step_history.py`

**文件内容**:
```python
# app/models/step_history.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StepHistory(Base):
    __tablename__ = "step_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("solve_sessions.id"))
    step: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)

    session = relationship("SolveSession", back_populates="step_history")
```

**验收**:
```bash
cd clarity-api
python -c "from app.models.step_history import StepHistory; print('OK')"
```

---

### Task 3: AnalyticsEvent Model

**目标**: 创建 `app/models/analytics_event.py`

**文件内容**:
```python
# app/models/analytics_event.py
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("solve_sessions.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**验收**:
```bash
cd clarity-api
python -c "from app.models.analytics_event import AnalyticsEvent; print('OK')"
```

---

### Task 4: AnalyticsService

**目标**: 创建 `app/services/analytics_service.py`

**文件内容**:
```python
# app/services/analytics_service.py
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics_event import AnalyticsEvent


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def emit(
        self,
        event_type: str,
        session_id: Optional[UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsEvent:
        event = AnalyticsEvent(
            event_type=event_type,
            session_id=session_id,
            payload=payload or {},
        )
        self.db.add(event)
        await self.db.flush()
        return event
```

**验收**:
```bash
cd clarity-api
python -c "from app.services.analytics_service import AnalyticsService; print('OK')"
```

---

### Task 5: StateMachine Service

**目标**: 创建 `app/services/state_machine.py`

**文件内容**:
```python
# app/services/state_machine.py
from typing import Optional

from app.models.solve_session import SolveStep


# 合法状态转换表
VALID_TRANSITIONS = {
    SolveStep.RECEIVE: [SolveStep.CLARIFY],
    SolveStep.CLARIFY: [SolveStep.REFRAME],
    SolveStep.REFRAME: [SolveStep.OPTIONS],
    SolveStep.OPTIONS: [SolveStep.COMMIT],
    SolveStep.COMMIT: [],  # 终态
}


def can_transition(current: SolveStep, next_step: SolveStep) -> bool:
    """检查状态转换是否合法"""
    return next_step in VALID_TRANSITIONS.get(current, [])


def get_next_step(current: SolveStep) -> Optional[SolveStep]:
    """获取下一个状态（如果唯一）"""
    valid = VALID_TRANSITIONS.get(current, [])
    return valid[0] if len(valid) == 1 else None


def is_final_step(step: SolveStep) -> bool:
    """检查是否为终态"""
    return step == SolveStep.COMMIT
```

**验收**:
```bash
cd clarity-api
python -c "
from app.services.state_machine import can_transition, get_next_step
from app.models.solve_session import SolveStep
assert can_transition(SolveStep.RECEIVE, SolveStep.CLARIFY) == True
assert can_transition(SolveStep.RECEIVE, SolveStep.OPTIONS) == False
assert get_next_step(SolveStep.RECEIVE) == SolveStep.CLARIFY
print('OK')
"
```

---

### Task 6: Update SolveSession Model

**目标**: 添加 step_history relationship 和新字段

**修改** `app/models/solve_session.py`:
```python
# 新增字段
locale: Mapped[str] = mapped_column(String(10), default="en")
first_step_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
reminder_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

# 新增 relationship
step_history = relationship("StepHistory", back_populates="session", lazy="selectin")
```

**验收**:
```bash
cd clarity-api
python -c "
from app.models.solve_session import SolveSession
print('locale' in SolveSession.__table__.columns)
print('OK')
"
```

---

### Task 7: Integrate State Machine in Router

**目标**: 修改 `app/routers/sessions.py`，集成状态机

**修改点**:
1. 导入 state_machine 和 AnalyticsService
2. 创建 session 时 emit `session_started`
3. 消息处理后检查 AI 返回的 `next_step`
4. 验证并执行状态转换
5. 记录 step_history
6. 转换时 emit `step_completed`
7. 完成时 emit `session_completed`

**验收**:
```bash
cd clarity-api
pytest tests/test_sessions.py -v -k "test_session_state_transition"
```

---

### Task 8: Enhance Step Prompts

**目标**: 完善 STEP_SYSTEM_PROMPTS

**修改** `app/routers/sessions.py` 中的 prompts:

```python
STEP_SYSTEM_PROMPTS = {
    SolveStep.RECEIVE.value: """You are Clarity, a supportive problem-solving coach.
In this RECEIVE phase, your goal is to listen deeply and reflect emotions.
- Mirror the user's feelings without judgment
- Use phrases like "I hear that..." or "It sounds like..."
- Do NOT offer solutions yet
- When emotion is fully expressed, set next_step to "clarify"
Respond in the user's language.""",

    SolveStep.CLARIFY.value: """You are in the CLARIFY phase.
Use the 5W1H framework to explore:
- Who is involved?
- What exactly happened?
- When did this start?
- Where does this occur?
- Why do you think this matters?
- How have you tried to address it?
After 3-5 exchanges or sufficient clarity, set next_step to "reframe".""",

    SolveStep.REFRAME.value: """You are in the REFRAME phase.
Help the user see the problem from a new angle using one technique:
- Devil's Advocate: What if the opposite were true?
- Zoom Out: How will this matter in 5 years?
- Best Friend Test: What would you tell a friend in this situation?
- Control Circle: What can you actually control here?
- Growth Lens: What could you learn from this?
When user accepts a new perspective, set next_step to "options".""",

    SolveStep.OPTIONS.value: """You are in the OPTIONS phase.
Generate 2-3 concrete options with brief trade-offs:
Option A: [Action] - Pros: ..., Cons: ...
Option B: [Action] - Pros: ..., Cons: ...
When user selects an option, set next_step to "commit".""",

    SolveStep.COMMIT.value: """You are in the COMMIT phase.
Help the user lock in their decision:
1. Confirm the chosen option
2. Define ONE concrete first step (specific action + time)
3. Offer an optional reminder
Return structured JSON in your response:
{"first_step": {"action": "...", "when": "..."}, "reminder": {"enabled": bool, "time": "...", "message": "..."}}
""",
}
```

**验收**:
```bash
cd clarity-api
python -c "
from app.routers.sessions import STEP_SYSTEM_PROMPTS
assert len(STEP_SYSTEM_PROMPTS) == 5
assert 'next_step' in STEP_SYSTEM_PROMPTS['receive']
print('OK')
"
```

---

### Task 9: Unit Tests for State Machine

**目标**: 创建 `tests/test_state_machine.py`

**文件内容**:
```python
import pytest
from app.models.solve_session import SolveStep
from app.services.state_machine import can_transition, get_next_step, is_final_step


class TestStateMachine:
    def test_valid_transitions(self):
        assert can_transition(SolveStep.RECEIVE, SolveStep.CLARIFY)
        assert can_transition(SolveStep.CLARIFY, SolveStep.REFRAME)
        assert can_transition(SolveStep.REFRAME, SolveStep.OPTIONS)
        assert can_transition(SolveStep.OPTIONS, SolveStep.COMMIT)

    def test_invalid_transitions(self):
        assert not can_transition(SolveStep.RECEIVE, SolveStep.OPTIONS)
        assert not can_transition(SolveStep.CLARIFY, SolveStep.COMMIT)
        assert not can_transition(SolveStep.COMMIT, SolveStep.RECEIVE)

    def test_get_next_step(self):
        assert get_next_step(SolveStep.RECEIVE) == SolveStep.CLARIFY
        assert get_next_step(SolveStep.COMMIT) is None

    def test_is_final_step(self):
        assert is_final_step(SolveStep.COMMIT)
        assert not is_final_step(SolveStep.RECEIVE)
```

**验收**:
```bash
cd clarity-api
pytest tests/test_state_machine.py -v
# 预期: 4 passed
```

---

### Task 10: Integration Tests

**目标**: 创建 `tests/test_solve_flow.py` 端到端测试

**测试场景**:
1. 创建 session → 状态为 receive
2. 发送消息 → AI 响应包含 next_step
3. 状态转换 → step_history 记录
4. 完成 5 步 → session 状态为 completed
5. analytics_events 包含所有事件

**验收**:
```bash
cd clarity-api
pytest tests/test_solve_flow.py -v
# 预期: 全部通过
```

---

## Task Dependency Graph

```
Task 1 (Migration)
    ↓
Task 2 (StepHistory) ──┬── Task 6 (Update SolveSession)
Task 3 (AnalyticsEvent)┘           ↓
    ↓                         Task 7 (Router Integration)
Task 4 (AnalyticsService)          ↓
    ↓                         Task 8 (Prompts)
Task 5 (StateMachine) ─────────────↓
                              Task 9 (Unit Tests)
                                   ↓
                              Task 10 (Integration Tests)
```

## Completion Checklist

- [ ] Task 1: Migration applied
- [ ] Task 2: StepHistory model created
- [ ] Task 3: AnalyticsEvent model created
- [ ] Task 4: AnalyticsService created
- [ ] Task 5: StateMachine service created
- [ ] Task 6: SolveSession updated
- [ ] Task 7: Router integrated
- [ ] Task 8: Prompts enhanced
- [ ] Task 9: Unit tests passing
- [ ] Task 10: Integration tests passing
- [ ] All tests pass: `pytest -v`
- [ ] Lint pass: `black . && ruff check .`
