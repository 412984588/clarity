# Epic 3 M1: Session + SSE - Task List

> **Based on**: docs/plan/epic-3-chat-plan.md
> **Created**: 2025-12-22

---

## Tasks

### T1: Create SolveSession Model
- [x] Create `app/models/solve_session.py`
- [x] Define SolveSession with: id, user_id, device_id, status, current_step, created_at, completed_at
- [x] Add SessionStatus and SolveStep enums
- [x] Export in `app/models/__init__.py`
- [x] Add `solve_sessions` relationship to User model

### T2: Database Migration
- [x] Generate Alembic migration: `alembic revision --autogenerate -m "add solve_sessions table"`
- [x] Review migration file
- [x] Run migration: `alembic upgrade head`

### T3: Create Session Schemas
- [x] Create `app/schemas/session.py`
- [x] Define SessionResponse
- [x] Define SessionListResponse with pagination
- [x] Define MessageRequest (content, step)
- [x] Define SSETokenEvent and SSEDoneEvent

### T4: Implement Session Router
- [x] Create `app/routers/sessions.py`
- [x] Implement `POST /sessions` - create session, return with usage info
- [x] Implement `GET /sessions` - list with pagination
- [x] Implement `GET /sessions/{id}` - get single session
- [x] Implement `POST /sessions/{id}/messages` - SSE streaming

### T5: SSE Streaming Logic
- [x] Create async generator for SSE events
- [x] Mock response: "I understand how you feel. Let me help you work through this."
- [x] Stream word-by-word with 50ms delay
- [x] Send done event with next_step and emotion_detected

### T6: Register Router
- [x] Import sessions router in `app/main.py`
- [x] Include router with prefix `/sessions`

### T7: Write Tests
- [x] Create `tests/test_sessions.py`
- [x] Test: unauthenticated returns 401
- [x] Test: create session returns 201
- [x] Test: list sessions returns array
- [x] Test: get session returns correct data
- [x] Test: get other user's session returns 404
- [x] Test: SSE endpoint returns event stream
- [x] Test: invalid session returns 404

### T8: Local Verification
- [x] Run `poetry run ruff check .`
- [x] Run `poetry run mypy app --ignore-missing-imports`
- [x] Run `poetry run pytest -v`
- [x] Run `npm run lint` in clarity-mobile
- [x] Run `npx tsc --noEmit` in clarity-mobile

---

## Completion Checklist

- [x] T1-T7 completed
- [x] T8 all checks pass
- [x] Git commit with proper message
- [x] PR created and merged
