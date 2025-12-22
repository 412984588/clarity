# Epic 5: Solve 5-Step Flow - 实现计划

**版本**: 1.0
**创建日期**: 2025-12-22

---

## 1. 总体架构

```
┌─────────────────────────────────────┐
│        Mobile (React Native)        │
│  ┌──────────────────────────────┐   │
│  │   SolveFlow Screen           │   │
│  │  - StepProgress              │   │
│  │  - MessageList               │   │
│  │  - OptionCards (Step 4)      │   │
│  │  - ActionCard (Step 5)       │   │
│  │  - EmotionBackground         │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   Local SQLite               │   │
│  │  - messages table            │   │
│  │  - options table             │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
              ↕ SSE / REST API
┌─────────────────────────────────────┐
│        Backend (FastAPI)            │
│  ┌──────────────────────────────┐   │
│  │   Sessions API               │   │
│  │  - POST /sessions            │   │
│  │  - GET /sessions/{id}/msg    │   │
│  │  - PATCH /sessions/{id} ✨   │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   State Machine              │   │
│  │  - validate_transition()     │   │
│  │  - next_step()               │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   Content Filter             │   │
│  │  - detect_injection()        │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   PostgreSQL                 │   │
│  │  - solve_sessions (metadata) │   │
│  │  - usage (concurrency safe)  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 2. 实现阶段

### Phase 1: Backend Foundation (优先级: 高)

**目标**: 建立 5-step 状态机和 PATCH API

**任务**:
1. 数据库迁移
   - 添加 \`locale\`, \`first_step_action\`, \`reminder_time\` 字段到 \`solve_sessions\`
   - 创建 alembic migration

2. 状态机实现
   - 创建 \`app/services/state_machine.py\`
   - 实现状态转换验证逻辑:
     \`\`\`python
     def validate_transition(current: SolveStep, next: SolveStep) -> bool:
         transitions = {
             SolveStep.RECEIVE: [SolveStep.CLARIFY],
             SolveStep.CLARIFY: [SolveStep.REFRAME],
             SolveStep.REFRAME: [SolveStep.OPTIONS],
             SolveStep.OPTIONS: [SolveStep.COMMIT],
             SolveStep.COMMIT: []  # 终态
         }
         return next in transitions.get(current, [])
     \`\`\`

3. PATCH /sessions/{id} 端点
   - 路由: \`app/routers/sessions.py\`
   - 验证: 状态转换合法性
   - 更新: session 字段（status, current_step, locale, etc.）

4. Prompt Injection 测试增强
   - 创建 \`tests/test_content_filter.py\`
   - 添加 4+ 测试用例覆盖绕过尝试

**验收**:
- \`poetry run pytest tests/test_sessions_patch.py -v\` 全通过
- \`poetry run pytest tests/test_content_filter.py -v\` 全通过
- \`poetry run mypy app\` 无错误

---

### Phase 2: Mobile SQLite & State (优先级: 高)

**目标**: 本地数据持久化和状态管理

**任务**:
1. SQLite 集成
   - 安装: \`expo-sqlite\`
   - 创建: \`src/services/database.ts\`
   - 初始化: 创建 \`messages\` 和 \`options\` 表
   - CRUD: \`insertMessage()\`, \`getMessages()\`, \`insertOption()\`, etc.

2. State Management
   - 使用 Context API 或 Zustand
   - State 结构:
     \`\`\`typescript
     interface SolveState {
       sessionId: string;
       currentStep: SolveStep;
       messages: Message[];
       options: Option[];
       selectedOptionId?: string;
       emotionDetected?: string;
     }
     \`\`\`

3. API Client
   - 修改 \`src/api/sessions.ts\`
   - 添加 \`patchSession(sessionId, updates)\`
   - SSE 消息接收后存入 SQLite

**验收**:
- SQLite 表创建成功
- 消息能正确存储和读取
- TypeScript 编译无错误: \`npx tsc --noEmit\`

---

### Phase 3: UI Components (优先级: 中)

**目标**: 实现 5-step 流程的 UI 组件

**任务**:
1. Step Progress Indicator
   - 创建: \`src/components/StepProgress.tsx\`
   - Props: \`currentStep: number\`, \`completedSteps: number[]\`
   - 样式: 横向点状指示器，当前步高亮

2. Option Cards (Step 4)
   - 创建: \`src/components/OptionCards.tsx\`
   - Props: \`options: Option[]\`, \`onSelect: (id) => void\`
   - 样式: 卡片式布局，选中时边框高亮
   - 交互: 点击选择，触发 \`onSelect\`

3. Action Card (Step 5)
   - 创建: \`src/components/ActionCard.tsx\`
   - Props: \`action: string\`, \`onSetReminder: () => void\`
   - 样式: 突出显示，带"Set Reminder"按钮

4. SolveFlow Screen
   - 修改: \`src/screens/SolveFlowScreen.tsx\`
   - 集成: StepProgress + MessageList + OptionCards + ActionCard
   - 逻辑: 根据 \`currentStep\` 显示对应组件

**验收**:
- 所有组件渲染正常
- 交互逻辑正确（选择 Option 后进入 Step 5）
- ESLint 无警告: \`npm run lint\`

---

### Phase 4: Emotion Background (优先级: 低)

**目标**: 根据情绪动态切换背景渐变

**任务**:
1. 安装依赖
   - \`npx expo install expo-linear-gradient\`

2. 背景组件
   - 创建: \`src/components/EmotionBackground.tsx\`
   - Props: \`emotion?: string\`
   - 逻辑: 根据 emotion 映射到颜色数组
   - 渲染: \`<LinearGradient colors={...} />\`

3. Settings 开关
   - 修改: \`src/screens/SettingsScreen.tsx\`
   - 添加: "Emotion Background" toggle
   - 存储: AsyncStorage (\`emotion_background_enabled\`)

**验收**:
- 情绪切换时背景正确变化
- Settings 开关能禁用/启用功能
- 动画流畅 (无卡顿)

---

### Phase 5: i18n (优先级: 中)

**目标**: 支持 en / es / zh 三语言

**任务**:
1. 安装库
   - \`npm install i18next react-i18next\`

2. 配置文件
   - 创建: \`src/i18n/index.ts\`
   - 初始化 i18next

3. 翻译文件
   - 创建: \`src/i18n/locales/en.json\`, \`es.json\`, \`zh.json\`
   - 添加 Spec 中定义的所有 key

4. 使用 Hook
   - 在组件中: \`const { t } = useTranslation();\`
   - 替换所有硬编码文案为: \`{t('solve.steps.receive')}\`

5. 语言切换
   - Settings 添加语言选择器
   - 调用 \`i18n.changeLanguage(locale)\`
   - 同步更新 backend: \`patchSession({ locale })\`

**验收**:
- 切换语言后 UI 文案正确更新
- 无硬编码文案（通过代码审查）
- 三种语言翻译完整

---

### Phase 6: Integration & Testing (优先级: 高)

**目标**: 端到端集成和全面测试

**任务**:
1. 集成测试
   - 创建新 session
   - 发送消息，推进 5 步
   - Step 4 选择 Option
   - Step 5 查看 Action Card
   - 验证本地 SQLite 数据

2. Backend 测试补全
   - \`tests/test_state_machine.py\` - 状态转换边界测试
   - \`tests/test_sessions_integration.py\` - 完整流程测试

3. Mobile 测试补全
   - \`__tests__/components/StepProgress.test.tsx\`
   - \`__tests__/components/OptionCards.test.tsx\`
   - \`__tests__/services/sqlite.test.ts\`

4. CI 验证
   - Backend: \`ruff + mypy + pytest\` 全绿
   - Mobile: \`lint + tsc\` 全绿

**验收**:
- 端到端流程无阻塞
- 所有测试通过
- CI/CD pipeline 绿色

---

## 3. 技术选型

| 模块 | 技术栈 | 理由 |
|------|--------|------|
| Mobile 状态管理 | Zustand / Context API | 轻量，满足需求 |
| 本地数据库 | expo-sqlite | Expo 官方支持，成熟稳定 |
| 渐变背景 | expo-linear-gradient | Expo 官方库，性能好 |
| i18n | react-i18next | React 生态标准方案 |
| Backend 状态机 | 自定义枚举 + 验证函数 | 简单直接，易测试 |
| 测试框架 | pytest (Backend) + Jest (Mobile) | 生态标准 |

---

## 4. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| SQLite 迁移复杂 | 高 | 提前编写迁移脚本，充分测试 |
| SSE 长连接不稳定 | 中 | 添加重连逻辑和心跳检测 |
| i18n 翻译不准确 | 低 | 使用 GPT-4 辅助翻译，人工审核 |
| Prompt Injection 绕过 | 高 | 多层防护，定期更新规则，渗透测试 |
| 并发 usage 计数错误 | 中 | 使用数据库事务和乐观锁 |

---

## 5. 里程碑

| 里程碑 | 预期完成 | 交付物 |
|--------|----------|--------|
| M1: Backend 基础 | Day 1 | PATCH API + 状态机 + 测试 |
| M2: Mobile 数据层 | Day 2 | SQLite + State + API Client |
| M3: UI 组件 | Day 3 | 5-step UI 完整实现 |
| M4: 增强功能 | Day 4 | 情绪背景 + i18n |
| M5: 测试与发布 | Day 5 | 端到端测试 + CI 全绿 |

---

## 6. 开发规范

### 6.1 Commit 规范
- Backend: \`feat(api): add PATCH /sessions endpoint\`
- Mobile: \`feat(solve): implement step progress indicator\`
- Tests: \`test(api): add prompt injection test cases\`

### 6.2 代码审查清单
- [ ] 无硬编码文案（必须用 i18n）
- [ ] 无 console.log（使用 logger）
- [ ] 类型安全（TypeScript 无 any）
- [ ] 测试覆盖（新增功能有测试）
- [ ] 无敏感信息（API Key, Token）
- [ ] 遵循项目代码风格（ruff, ESLint）

### 6.3 测试策略
- **单元测试**: 覆盖状态机、content filter、SQLite CRUD
- **集成测试**: 覆盖 PATCH API、SSE 流程
- **端到端测试**: 手动测试完整 5-step 流程

---

**批准**: 待确认后按阶段执行
