# Epic 3 M1: Session + SSE - Implementation Plan

> **Based on**: docs/spec/epic-3-chat.md
> **Created**: 2025-12-22

---

## Implementation Phases

### Phase 1: Database Model

1. Create `SolveSession` model in `app/models/solve_session.py`
2. Add relationship to `User` model
3. Create Alembic migration
4. Run migration to create table

### Phase 2: Schemas

1. Create `app/schemas/session.py` with:
   - `SessionCreate` (empty for now)
   - `SessionResponse`
   - `SessionListResponse`
   - `MessageRequest`
   - `SSETokenEvent`
   - `SSEDoneEvent`

### Phase 3: Router Implementation

1. Create `app/routers/sessions.py` with:
   - `POST /sessions` - Create session
   - `GET /sessions` - List sessions with pagination
   - `GET /sessions/{id}` - Get single session
   - `POST /sessions/{id}/messages` - SSE streaming

2. Register router in `app/main.py`

### Phase 4: SSE Streaming

1. Implement SSE generator function
2. Use `StreamingResponse` with `text/event-stream` media type
3. Mock token streaming with delays
4. Send `done` event with metadata

### Phase 5: Testing

1. Create `tests/test_sessions.py` with:
   - Auth requirement tests
   - Session CRUD tests
   - SSE behavior tests

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/models/solve_session.py` | Create | SolveSession model |
| `app/models/__init__.py` | Modify | Export SolveSession |
| `app/models/user.py` | Modify | Add relationship |
| `alembic/versions/xxx.py` | Create | Migration for solve_sessions |
| `app/schemas/session.py` | Create | Request/Response schemas |
| `app/routers/sessions.py` | Create | Session endpoints |
| `app/main.py` | Modify | Register sessions router |
| `tests/test_sessions.py` | Create | Session tests |

---

## Technical Decisions

### SSE Format

```python
async def sse_generator():
    for word in response.split():
        yield f"event: token\ndata: {json.dumps({'content': word})}\n\n"
        await asyncio.sleep(0.05)
    yield f"event: done\ndata: {json.dumps({'next_step': 'clarify', 'emotion_detected': 'neutral'})}\n\n"
```

### Pagination

- Default limit: 20
- Max limit: 100
- Offset-based pagination

### Status Enum

```python
class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
```

### Step Enum

```python
class SolveStep(str, Enum):
    RECEIVE = "receive"
    CLARIFY = "clarify"
    REFRAME = "reframe"
    OPTIONS = "options"
    COMMIT = "commit"
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SSE connection drops | Medium | Client handles reconnection (M2+) |
| Large session list | Low | Pagination implemented |
| Race conditions | Low | Single-server, DB transactions |

---

## Success Criteria

- [ ] All 4 endpoints functional
- [ ] SSE streaming works correctly
- [ ] Tests pass (ruff, mypy, pytest)
- [ ] Mobile CI passes (lint, tsc)
