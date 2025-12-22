# Epic 3 M1: Session + SSE - Task List

> **Based on**: docs/plan/epic-3-chat-plan.md
> **Created**: 2025-12-22

---

## Tasks

### T1: Create SolveSession Model
- [ ] Create `app/models/solve_session.py`
- [ ] Define SolveSession with: id, user_id, device_id, status, current_step, created_at, completed_at
- [ ] Add SessionStatus and SolveStep enums
- [ ] Export in `app/models/__init__.py`
- [ ] Add `solve_sessions` relationship to User model

### T2: Database Migration
- [ ] Generate Alembic migration: `alembic revision --autogenerate -m "add solve_sessions table"`
- [ ] Review migration file
- [ ] Run migration: `alembic upgrade head`

### T3: Create Session Schemas
- [ ] Create `app/schemas/session.py`
- [ ] Define SessionResponse
- [ ] Define SessionListResponse with pagination
- [ ] Define MessageRequest (content, step)
- [ ] Define SSETokenEvent and SSEDoneEvent

### T4: Implement Session Router
- [ ] Create `app/routers/sessions.py`
- [ ] Implement `POST /sessions` - create session, return with usage info
- [ ] Implement `GET /sessions` - list with pagination
- [ ] Implement `GET /sessions/{id}` - get single session
- [ ] Implement `POST /sessions/{id}/messages` - SSE streaming

### T5: SSE Streaming Logic
- [ ] Create async generator for SSE events
- [ ] Mock response: "I understand how you feel. Let me help you work through this."
- [ ] Stream word-by-word with 50ms delay
- [ ] Send done event with next_step and emotion_detected

### T6: Register Router
- [ ] Import sessions router in `app/main.py`
- [ ] Include router with prefix `/sessions`

### T7: Write Tests
- [ ] Create `tests/test_sessions.py`
- [ ] Test: unauthenticated returns 401
- [ ] Test: create session returns 201
- [ ] Test: list sessions returns array
- [ ] Test: get session returns correct data
- [ ] Test: get other user's session returns 404
- [ ] Test: SSE endpoint returns event stream
- [ ] Test: invalid session returns 404

### T8: Local Verification
- [ ] Run `poetry run ruff check .`
- [ ] Run `poetry run mypy app --ignore-missing-imports`
- [ ] Run `poetry run pytest -v`
- [ ] Run `npm run lint` in clarity-mobile
- [ ] Run `npx tsc --noEmit` in clarity-mobile

---

## Completion Checklist

- [ ] T1-T7 completed
- [ ] T8 all checks pass
- [ ] Git commit with proper message
- [ ] PR created and merged
