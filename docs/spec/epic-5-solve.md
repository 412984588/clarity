# Epic 5: Solve 5-Step Main Flow - Specification

## Overview

实现 Clarity 的核心功能：5 步解决问题框架。用户通过 Receive → Clarify → Reframe → Options → Commit 流程，获得情绪支持并找到可执行的解决方案。

## Functional Requirements

### FR-1: State Machine

| Current State | Trigger | Next State | Side Effects |
|---------------|---------|------------|--------------|
| `receive` | AI 判断情绪已充分表达 | `clarify` | emit `step_completed` |
| `clarify` | 5W1H 完成或达到 5 轮 | `reframe` | emit `step_completed` |
| `reframe` | 用户接受重构视角 | `options` | emit `step_completed` |
| `options` | 用户选择方案 | `commit` | emit `option_selected` |
| `commit` | 用户确认行动 | completed | emit `session_completed` |
| any | 用户主动退出 | abandoned | emit `session_abandoned` |

状态转换由后端 AI 响应中的 `next_step` 字段驱动。

### FR-2: Step-Specific Prompts

每个步骤使用专用 system prompt：

| Step | 目标 | 关键指令 |
|------|------|----------|
| **Receive** | 倾听+共情 | 反映情绪，不急于解决问题 |
| **Clarify** | 5W1H 探索 | Who/What/When/Where/Why/How |
| **Reframe** | 换视角 | Devil's Advocate / Zoom Out / Best Friend Test / Control Circle / Growth Lens |
| **Options** | 生成方案 | 2-3 选项，含 pros/cons |
| **Commit** | 锁定行动 | 明确 first step + optional reminder |

### FR-3: Commit Step Output

Commit 步骤的 AI 响应必须包含结构化数据：

```json
{
  "first_step": {
    "action": "明天早上 9 点给老板发邮件，主题：关于项目延期的讨论",
    "when": "2024-01-15T09:00:00Z"
  },
  "reminder": {
    "enabled": true,
    "time": "2024-01-15T08:45:00Z",
    "message": "准备好邮件内容，深呼吸，你可以的"
  },
  "summary": "你决定通过主动沟通来解决项目压力问题"
}
```

### FR-4: Internationalization (i18n)

支持三种语言：EN / ES / zh-Hans

| 类型 | 实现方式 |
|------|----------|
| Error Codes | JSON 映射表 `errors/{lang}.json` |
| System Prompts | 模板变量 + 语言检测 |
| UI Strings | 前端 i18n 库 |

后端根据 `Accept-Language` header 或用户 locale 设置返回对应语言。

### FR-5: Safety & Crisis Diversion

复用现有 `content_filter.py` 机制：

1. **危机关键词检测**：suicide, self-harm, 自杀, 自伤 等
2. **触发行为**：
   - 暂停 AI 响应
   - 返回危机资源（热线号码等）
   - 记录 `crisis_detected` 事件
3. **Prompt Injection 防护**：过滤 `ignore previous`, `system:` 等模式

### FR-6: Analytics Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `session_started` | 创建新 session | `{session_id, user_id, device_id}` |
| `step_completed` | 状态转换 | `{session_id, from_step, to_step, duration_ms}` |
| `session_completed` | 到达 commit 并确认 | `{session_id, total_duration_ms, steps_count}` |
| `session_abandoned` | 用户主动退出或超时 | `{session_id, last_step, reason}` |
| `option_selected` | 用户在 Options 选择 | `{session_id, option_index, option_summary}` |
| `reminder_set` | 用户设置提醒 | `{session_id, reminder_time}` |
| `crisis_detected` | 危机关键词命中 | `{session_id, keyword_category}` |

## Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Latency (first token) | < 500ms |
| Session timeout | 30 min inactive |
| Max messages per step | 10 |
| AI response max tokens | 1024 |

## API Changes

### POST /sessions
- 新增可选参数 `locale: string` (default: "en")
- Response 新增 `analytics_id: string`

### POST /sessions/{id}/messages
- Request body 新增 `metadata: object` (optional)
- SSE Done event 新增 `emotion_detected`, `structured_output`

### GET /sessions/{id}
- Response 新增 `step_history: array`, `analytics: object`

## Database Changes

```sql
-- 新增 step_history 表
CREATE TABLE step_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES solve_sessions(id),
    step VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    message_count INT DEFAULT 0
);

-- 新增 analytics_events 表
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES solve_sessions(id),
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- solve_sessions 新增字段
ALTER TABLE solve_sessions ADD COLUMN locale VARCHAR(10) DEFAULT 'en';
ALTER TABLE solve_sessions ADD COLUMN first_step_action TEXT;
ALTER TABLE solve_sessions ADD COLUMN reminder_time TIMESTAMP;
```

## Out of Scope (Wave 1)

- Push notification 实际发送
- Reminder 持久化调度
- 多语言 prompt 完整翻译
- Options 的 A/B testing
