# Epic 5: Solve 5-Step - Implementation Plan

## Wave 分解

### Wave 1: Minimal Happy Path (本次实现)

**目标**: Step 1→2→3→4→5 完整流程可跑通

| Layer | 任务 |
|-------|------|
| **DB** | step_history 表 + analytics_events 表 |
| **Model** | StepHistory, AnalyticsEvent SQLAlchemy models |
| **Service** | AnalyticsService.emit() 方法 |
| **Router** | 状态机逻辑 + step 自动转换 |
| **Prompt** | 完善 5 步 system prompts |
| **Test** | 端到端 happy path 测试 |

### Wave 2: i18n + Safety (后续)

- 多语言 error codes
- 多语言 prompt 模板
- 危机检测增强
- 危机资源响应

### Wave 3: Commit 结构化输出 (后续)

- AI 返回 JSON 格式 first_step
- Reminder 时间解析
- 前端 Commit 卡片 UI

### Wave 4: Analytics 完善 (后续)

- 完整事件追踪
- 仪表板集成
- A/B testing 支持

## 技术决策

### D1: 状态机实现

**选项**:
- A) 纯 Python if-else
- B) transitions 库
- C) 自定义 StateMachine 类

**决定**: A) 纯 Python if-else
- 原因：状态数量少（5个），逻辑简单，无需引入依赖

### D2: Analytics 事件存储

**选项**:
- A) 直接写 DB
- B) 消息队列 (Redis/RabbitMQ)
- C) 异步任务 (Celery)

**决定**: A) 直接写 DB
- 原因：MVP 阶段，事件量小，简化架构

### D3: AI 判断状态转换

**选项**:
- A) AI 在响应中返回 next_step
- B) 后端规则判断（消息数、关键词）
- C) 混合：AI 建议 + 后端校验

**决定**: C) 混合模式
- AI 返回建议的 next_step
- 后端校验转换合法性（防止跳步）

### D4: i18n 架构

**选项**:
- A) 后端全处理，返回翻译后文本
- B) 后端返回 key，前端翻译
- C) 混合：error codes 前端翻译，AI prompt 后端处理

**决定**: C) 混合模式
- error codes: `{"error": "SESSION_LIMIT_REACHED", "params": {"limit": 5}}`
- 前端根据 locale 翻译

## 文件变更清单

### 新增文件

```
clarity-api/
├── app/
│   ├── models/
│   │   ├── step_history.py      # StepHistory model
│   │   └── analytics_event.py   # AnalyticsEvent model
│   ├── services/
│   │   ├── analytics_service.py # 事件发送
│   │   └── state_machine.py     # 状态转换逻辑
│   └── schemas/
│       └── analytics.py         # Event schemas
├── alembic/versions/
│   └── xxx_add_step_history.py  # Migration
└── tests/
    ├── test_state_machine.py
    └── test_analytics.py
```

### 修改文件

```
clarity-api/
├── app/
│   ├── routers/sessions.py      # 集成状态机
│   └── models/solve_session.py  # 新增字段
└── tests/
    └── test_sessions.py         # 扩展测试
```

## 依赖关系

```
DB Migration
    ↓
StepHistory Model ──┐
                    ├── AnalyticsService
AnalyticsEvent ─────┘
    ↓
StateMachine
    ↓
Sessions Router
    ↓
Tests
```

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| AI 返回错误 next_step | 状态混乱 | 后端校验 + 默认值 |
| 高并发事件写入 | DB 压力 | 批量写入 / 异步队列 (Wave 4) |
| Prompt 过长 | Token 超限 | 分步骤精简 + 截断历史 |

## 验收标准

Wave 1 完成标志：

1. ✅ `POST /sessions` 返回 session，状态为 receive
2. ✅ `POST /sessions/{id}/messages` 循环对话
3. ✅ AI 返回 `next_step` 触发状态转换
4. ✅ step_history 表记录每步开始/结束
5. ✅ analytics_events 表记录关键事件
6. ✅ 完成 5 步后 session 状态变为 completed
7. ✅ 全部测试通过 (`pytest -v`)
