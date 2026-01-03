# 🚀 Orchestrator 启动指南

## 快速启动流程

### 方式 1：恢复现有会话（推荐）

如果你的 `ai-commander` 会话还在运行：

```bash
# 查看现有会话
tmux ls

# 连接到现有会话
tmux attach -t ai-commander

# 或简写
tmux a -t ai-commander
```

---

### 方式 2：从零启动新会话

#### 步骤 1：创建 tmux 会话

```bash
# 创建名为 ai-commander 的会话
tmux new-session -s ai-commander -n control

# 你现在在 Window 0 (control)
```

#### 步骤 2：启动 Orchestrator（你 - Claude Code）

```bash
# 在 Window 0 启动 Claude Code
claude

# 进入后，告诉我你的身份
"You are the Orchestrator managing multiple AI agents for the Solacore project."
```

#### 步骤 3：创建 Worker 窗口

在 tmux 中按快捷键创建窗口：

```bash
# 创建 Window 1 (Claude Worker)
Ctrl+b c
claude

# 创建 Window 2 (Codex Worker)
Ctrl+b c
codex --yolo

# 创建 Window 3 (Gemini Worker)
Ctrl+b c
gemini --yolo

# 创建 Window 4 (Codex Worker 2)
Ctrl+b c
codex --yolo
```

#### 步骤 4：切换回 Orchestrator 窗口

```bash
# 按快捷键切回 Window 0
Ctrl+b 0
```

现在你有：
```
ai-commander session
├─ Window 0: Claude Code (Orchestrator - 你)
├─ Window 1: Claude Code (Worker)
├─ Window 2: Codex (Engineer)
├─ Window 3: Gemini (Reviewer)
└─ Window 4: Codex (Engineer 2)
```

---

### 方式 3：自动化脚本启动（高级）

创建启动脚本 `~/start-orchestrator.sh`：

```bash
#!/bin/bash

# 创建会话
tmux new-session -d -s ai-commander -n control

# Window 0: Orchestrator
tmux send-keys -t ai-commander:0 "claude" C-m
sleep 2
tmux send-keys -t ai-commander:0 "You are the Orchestrator managing AI agents for Solacore project" C-m

# Window 1: Claude Worker
tmux new-window -t ai-commander:1 -n claude-worker
tmux send-keys -t ai-commander:1 "cd ~/Documents/claude/clarity && claude" C-m

# Window 2: Codex Worker
tmux new-window -t ai-commander:2 -n codex-1
tmux send-keys -t ai-commander:2 "cd ~/Documents/claude/clarity && codex --yolo" C-m

# Window 3: Gemini Worker
tmux new-window -t ai-commander:3 -n gemini
tmux send-keys -t ai-commander:3 "cd ~/Documents/claude/clarity && gemini --yolo" C-m

# Window 4: Codex Worker 2
tmux new-window -t ai-commander:4 -n codex-2
tmux send-keys -t ai-commander:4 "cd ~/Documents/claude/clarity && codex --yolo" C-m

# 切回 Window 0
tmux select-window -t ai-commander:0

# 连接到会话
tmux attach -t ai-commander
```

使用方法：
```bash
chmod +x ~/start-orchestrator.sh
~/start-orchestrator.sh
```

---

## 使用 Orchestrator 命令

### 发送任务给 Agent

```bash
# 在任何终端窗口（不需要在 tmux 里）
send-message ai-commander:2 "你的任务"

# 或在 tmux 的 Orchestrator 窗口里
send-message ai-commander:3 "实现新功能"
```

### 调度定时检查

```bash
# 30 分钟后检查
schedule-check 30 "检查进度并分配下一个任务"

# 1 小时后汇总
schedule-check 60 "收集所有结果"
```

---

## 检查当前状态

### 查看所有 tmux 会话

```bash
tmux ls
```

### 查看会话的窗口列表

```bash
# 在 tmux 外部
tmux list-windows -t ai-commander

# 在 tmux 内部
Ctrl+b w  # 显示窗口选择器
```

### 查看某个窗口的内容

```bash
# 不进入窗口，捕获输出
tmux capture-pane -t ai-commander:2 -p -S -30
```

### 切换窗口（在 tmux 内）

```bash
Ctrl+b 0  # 切到 Window 0
Ctrl+b 1  # 切到 Window 1
Ctrl+b 2  # 切到 Window 2
# ...以此类推
```

---

## 关闭和清理

### 杀掉单个窗口

```bash
# 在 tmux 内
Ctrl+b &  # 杀掉当前窗口

# 在 tmux 外
tmux kill-window -t ai-commander:2
```

### 杀掉整个会话

```bash
tmux kill-session -t ai-commander
```

---

## 日常工作流

### 早上启动

```bash
# 1. 检查是否有会话
tmux ls

# 2. 如果有，连接
tmux attach -t ai-commander

# 3. 如果没有，创建新的
~/start-orchestrator.sh  # 如果你创建了脚本
# 或手动创建（参考方式 2）
```

### 分配任务

```bash
# 在 Orchestrator 窗口（Window 0），我会帮你发送命令
# 或者你自己在任何终端发送：
send-message ai-commander:2 "Implement feature X"
send-message ai-commander:3 "Review code in file Y"
```

### 检查进度

```bash
# 方法 1：切换窗口查看（手动）
Ctrl+b 2  # 查看 Codex
Ctrl+b 3  # 查看 Gemini

# 方法 2：捕获输出（自动）
tmux capture-pane -t ai-commander:2 -p -S -20
tmux capture-pane -t ai-commander:3 -p -S -20
```

### 晚上结束

```bash
# 方法 1：Detach（会话继续运行）
Ctrl+b d

# 方法 2：杀掉会话
tmux kill-session -t ai-commander
```

---

## 故障排查

### 问题：tmux 会话丢失

**检查**：
```bash
tmux ls
```

**解决**：
- 如果没有会话，按"方式 2"重新创建
- 如果有会话但连接不上，尝试 `tmux kill-server` 然后重启

### 问题：send-message 命令找不到

**检查**：
```bash
which send-message
```

**解决**：
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

### 问题：Agent 没有响应

**检查窗口状态**：
```bash
tmux capture-pane -t ai-commander:2 -p -S -10
```

**原因**：可能在处理其他任务，等待或重启

---

## 高级技巧

### 同时查看多个窗口

```bash
# 在 tmux 内，分割窗格
Ctrl+b %  # 垂直分割
Ctrl+b "  # 水平分割

# 然后在每个窗格连接不同窗口
# 窗格 1
tmux join-pane -s ai-commander:2

# 窗格 2
tmux join-pane -s ai-commander:3
```

### 保存和恢复布局

```bash
# 保存当前布局
tmux list-windows -t ai-commander > ~/tmux-layout.txt

# 恢复时参考此文件重建
```

---

## 常用快捷键速查

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+b c` | 创建新窗口 |
| `Ctrl+b 0-9` | 切换到窗口 0-9 |
| `Ctrl+b w` | 窗口列表 |
| `Ctrl+b &` | 杀掉当前窗口 |
| `Ctrl+b d` | Detach 会话 |
| `Ctrl+b %` | 垂直分割窗格 |
| `Ctrl+b "` | 水平分割窗格 |
| `Ctrl+b 方向键` | 切换窗格 |

---

## 总结

**最简单的启动方式**：
```bash
# 1. 连接现有会话
tmux attach -t ai-commander

# 2. 如果没有，创建新会话并手动启动 agents
tmux new -s ai-commander
claude  # Window 0
Ctrl+b c && codex --yolo  # Window 1
Ctrl+b c && gemini --yolo  # Window 2
# ...

# 3. 使用 Orchestrator 命令
send-message ai-commander:1 "任务"
schedule-check 30 "检查"
```

**记住这两个命令**：
- `send-message` - 发送任务
- `schedule-check` - 定时检查

现在你随时可以启动和使用 Orchestrator 了！ 🚀
