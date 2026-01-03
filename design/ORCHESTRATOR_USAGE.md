# 🤖 Tmux Orchestrator 使用指南

## 安装完成 ✅

已配置 Tmux-Orchestrator 用于管理多 AI 协作

---

## 🎯 我们的团队架构

```
ai-commander session
├─ Window 1: Claude Code (我 - Orchestrator)
├─ Window 2: Claude Code (Worker)
├─ Window 3: Codex (Engineer)
├─ Window 4: Gemini (Reviewer)
└─ Window 5: Codex (Engineer 2)
```

---

## 🔧 核心命令

### 1. 发送消息给任意 Agent

```bash
# 完整命令
/Users/zhimingdeng/Tmux-Orchestrator/send-claude-message.sh ai-commander:3 "你的任务"

# 简化命令（推荐）
send-message ai-commander:3 "你的任务"
send-message ai-commander:4 "审查这段代码"
send-message ai-commander:5 "修复这个 Bug"
```

**参数说明**：
- `ai-commander:3` = session名:窗口号
- 消息内容用引号包裹

**示例**：
```bash
# 让 Codex 实现功能
send-message ai-commander:3 "Add /health endpoint with database check"

# 让 Gemini 审查代码
send-message ai-commander:4 "Review the code in app/routers/templates.py"

# 让 Claude Worker 写文档
send-message ai-commander:2 "Update README with new features"
```

---

### 2. 调度定时检查

```bash
# 完整命令
/Users/zhimingdeng/Tmux-Orchestrator/schedule_with_note.sh <分钟> "<备注>" [目标窗口]

# 简化命令（推荐）
schedule-check 30 "检查 Codex 的进度"
schedule-check 60 "收集所有 Agent 的结果" ai-commander:1
```

**参数说明**：
- `30` = 多少分钟后执行
- `"备注"` = 提醒自己要做什么
- `ai-commander:1` = 可选，默认是当前窗口

**示例**：
```bash
# 30 分钟后检查进度
schedule-check 30 "Review Codex's health endpoint implementation"

# 1 小时后汇总结果
schedule-check 60 "Collect results from all agents and create summary report"

# 2 小时后 Git 提交
schedule-check 120 "Commit all changes and push to remote"
```

---

## 📋 实战工作流

### 场景 1：并行开发新功能

```bash
# 1. 分配任务
send-message ai-commander:3 "Implement user profile endpoint GET /api/users/me"
send-message ai-commander:5 "Write tests for user profile endpoint"

# 2. 调度检查
schedule-check 30 "Check if both agents completed their tasks"

# 3. 30分钟后我会收到提醒，然后检查进度
# 4. 如果完成，让 Gemini 审查
send-message ai-commander:4 "Review user profile implementation in ai-commander:3"
```

---

### 场景 2：修复 Bug

```bash
# 1. 诊断问题
send-message ai-commander:3 "Debug why /auth/login returns 500 error"

# 2. 同时让另一个 Codex 检查日志
send-message ai-commander:5 "Check error logs for /auth/login failures"

# 3. 调度 15 分钟检查
schedule-check 15 "Review bug diagnosis from both Codex instances"

# 4. 收到提醒后，分配修复任务
send-message ai-commander:3 "Fix the authentication bug based on findings"

# 5. 让 Gemini 验证
send-message ai-commander:4 "Verify the bug fix is complete and test coverage is good"
```

---

### 场景 3：代码审查 + 优化

```bash
# 1. 让 Gemini 审查整个模块
send-message ai-commander:4 "Review app/services/auth_service.py for security issues"

# 2. 等待 5 分钟
schedule-check 5 "Check Gemini's review results"

# 3. 根据审查结果，让 Codex 优化
send-message ai-commander:3 "Refactor auth_service.py based on Gemini's review"

# 4. 最终验证
schedule-check 20 "Run all tests and verify refactoring is complete"
```

---

## 🎓 高级技巧

### 技巧 1：链式任务执行

```bash
# 发送多个消息形成任务链
send-message ai-commander:3 "Step 1: Create database migration for templates table"
sleep 30
send-message ai-commander:3 "Step 2: Implement PromptTemplate model"
sleep 30
send-message ai-commander:3 "Step 3: Create API endpoints for templates"
```

### 技巧 2：并行 + 汇总

```bash
# T=0: 分配并行任务
send-message ai-commander:3 "Task A: Backend API"
send-message ai-commander:5 "Task B: Frontend UI"
send-message ai-commander:2 "Task C: Documentation"

# T+30: 调度汇总
schedule-check 30 "Collect all results and integrate"

# T+30 收到提醒后，我会：
# 1. 检查所有窗口的输出
# 2. 整合结果
# 3. 创建统一的 PR
```

### 技巧 3：自动 Git 提交循环

```bash
# 每 30 分钟自动提交
schedule-check 30 "Auto-commit progress and schedule next commit"

# 在我的检查逻辑中：
# 1. 检查 git status
# 2. 如果有改动，自动 commit
# 3. 再次调度 30 分钟后的检查
# 形成无限循环
```

---

## 📊 监控所有 Agent

### 快速查看所有窗口

```bash
# 方法 1：切换窗口查看（手动）
Ctrl+b 3  # 查看 Codex Window 3
Ctrl+b 4  # 查看 Gemini Window 4
Ctrl+b 5  # 查看 Codex Window 5

# 方法 2：捕获输出（自动）
tmux capture-pane -t ai-commander:3 -p -S -30  # 最近 30 行
tmux capture-pane -t ai-commander:4 -p -S -30
tmux capture-pane -t ai-commander:5 -p -S -30
```

---

## 🚨 故障排查

### 问题 1：send-message 命令找不到

**解决**：
```bash
export PATH="$HOME/.local/bin:$PATH"

# 或永久添加到 .zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 问题 2：定时检查没有触发

**检查**：
```bash
# 查看后台进程
ps aux | grep schedule

# 查看调度备注文件
cat /Users/zhimingdeng/Tmux-Orchestrator/next_check_note.txt
```

### 问题 3：消息发送后 Agent 没响应

**原因**：Agent 可能在处理其他任务

**解决**：
```bash
# 等待一会再发送
sleep 5
send-message ai-commander:3 "Your message"

# 或者检查窗口状态
tmux capture-pane -t ai-commander:3 -p -S -10
```

---

## 📚 最佳实践

1. **清晰的任务描述**
   - ✅ "Implement GET /api/templates with category filter"
   - ❌ "Add templates"

2. **合理的时间间隔**
   - 简单任务：5-10 分钟
   - 中等任务：20-30 分钟
   - 复杂任务：60+ 分钟

3. **定期汇总**
   - 每小时收集一次所有 Agent 的进度
   - 每天结束前创建总结报告

4. **自动化循环**
   - Git 提交：每 30 分钟
   - 测试运行：每次代码改动后
   - 进度检查：每小时

---

## 🎯 下一步

现在你（老板）可以：

1. **直接发命令**：
   ```bash
   send-message ai-commander:3 "你的任务"
   ```

2. **我（Claude Code）会**：
   - 监控所有 Agent 的进度
   - 定时检查和汇总结果
   - 处理错误和重试
   - 最终给你报告

3. **你只需要**：
   - 告诉我总体目标
   - 我会自动编排和管理 AI 团队

---

**Orchestrator 已就绪，随时待命！** 🚀
