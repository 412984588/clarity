# Epic 3: Chat Core & AI Integration - Specification

> **Version**: 1.0
> **Last Updated**: 2025-12-22
> **Status**: Draft
> **Scope**: M1 - Session Management + SSE Framework

---

## Overview

Epic 3 builds the core chat infrastructure for Clarity's Solve problem-solving sessions. M1 focuses on backend session management and SSE streaming scaffold (without real LLM integration).

---

## M1 Scope: Session Management + SSE Framework

### Objectives

1. **Solve Session CRUD**: Create, retrieve, and list problem-solving sessions
2. **SSE Streaming Scaffold**: Server-Sent Events endpoint for streaming AI responses (mock data)
3. **Authentication Integration**: All endpoints require valid JWT + device binding
4. **Usage Tracking**: Session creation increments usage counter

---

## API Endpoints

### 1. POST /sessions

Create a new Solve session.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)
- `X-Device-Fingerprint: <fingerprint>` (required)

**Request Body:**
```json
{}
```

**Response (201):**
```json
{
  "session_id": "uuid",
  "status": "active",
  "current_step": "receive",
  "created_at": "2025-12-22T10:00:00Z",
  "usage": {
    "sessions_used": 3,
    "sessions_limit": 10,
    "tier": "free"
  }
}
```

**Error Codes:**
- `401 INVALID_TOKEN` - Missing or invalid JWT
- `403 QUOTA_EXCEEDED` - Session limit reached
- `403 DEVICE_LIMIT_REACHED` - Device limit exceeded

---

### 2. GET /sessions

List user's Solve sessions (most recent first).

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Query Parameters:**
- `limit` (optional, default=20, max=100)
- `offset` (optional, default=0)

**Response (200):**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "status": "active",
      "current_step": "clarify",
      "created_at": "2025-12-22T10:00:00Z",
      "completed_at": null
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

---

### 3. GET /sessions/{id}

Get a specific session's metadata.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Response (200):**
```json
{
  "id": "uuid",
  "status": "active",
  "current_step": "receive",
  "created_at": "2025-12-22T10:00:00Z",
  "completed_at": null
}
```

**Error Codes:**
- `404 SESSION_NOT_FOUND` - Session doesn't exist or belongs to another user

---

### 4. POST /sessions/{id}/messages (SSE)

Send a message and receive streaming AI response via Server-Sent Events.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)
- `Content-Type: application/json`
- `Accept: text/event-stream`

**Request Body:**
```json
{
  "content": "I'm frustrated with my job...",
  "step": "receive"
}
```

**Response (200, SSE Stream):**
```
event: token
data: {"content": "I"}

event: token
data: {"content": " understand"}

event: token
data: {"content": " how"}

event: token
data: {"content": " you"}

event: token
data: {"content": " feel."}

event: done
data: {"next_step": "clarify", "emotion_detected": "frustrated"}
```

**Error Codes:**
- `404 SESSION_NOT_FOUND` - Invalid session
- `400 SESSION_COMPLETED` - Session already finished

---

## Data Model

### SolveSession (New Table)

```sql
CREATE TABLE solve_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id UUID REFERENCES devices(id),
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, abandoned
    current_step VARCHAR(50) DEFAULT 'receive',  -- receive, clarify, reframe, options, commit
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_solve_sessions_user ON solve_sessions(user_id);
CREATE INDEX idx_solve_sessions_status ON solve_sessions(user_id, status);
```

---

## Middleware Chain

All session endpoints must pass through:

1. `AuthMiddleware` - Verify JWT, extract user_id
2. `DeviceMiddleware` - Validate device fingerprint (already implemented)
3. `SubscriptionMiddleware` - Check quota before session creation (future M2+)
4. `RateLimitMiddleware` - Per-user rate limiting (future M2+)

For M1, only `AuthMiddleware` is strictly required.

---

## SSE Implementation Notes

### M1 Mock Behavior

Since M1 doesn't integrate real LLM, the SSE endpoint will:

1. Accept the message content
2. Generate a mock response by splitting a placeholder text into tokens
3. Stream tokens with 50ms delay between each
4. Send `done` event with mock `next_step` and `emotion_detected`

### Mock Response Example

```python
MOCK_RESPONSE = "I understand how you feel. Let me help you work through this."
```

Split into tokens and streamed word-by-word.

---

## Security Considerations

1. **Session Ownership**: Users can only access their own sessions
2. **Device Binding**: Sessions are linked to the device that created them
3. **Token Validation**: JWT must be valid and session must be active
4. **No Content Storage**: Message content is NOT stored on server (privacy-first)

---

## Testing Strategy (Minimum)

### Required Tests

1. **Auth Tests**:
   - Unauthenticated request returns 401
   - Invalid token returns 401

2. **Session CRUD Tests**:
   - Create session returns 201 with correct structure
   - Get session returns correct data
   - List sessions returns paginated results
   - Access other user's session returns 404

3. **SSE Tests**:
   - SSE endpoint returns proper event stream
   - Stream includes token events and done event
   - Invalid session returns 404

---

## Dependencies

- FastAPI with `StreamingResponse` for SSE
- SQLAlchemy async for database operations
- Existing auth middleware (`get_current_user`)

---

## Out of Scope (M2+)

- Real LLM integration (OpenAI/Claude)
- PII stripping before AI calls
- Token usage tracking per request
- Subscription quota enforcement
- Rate limiting
- PATCH /sessions/{id} for status updates

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-22 | 1.0 | Initial M1 specification |
