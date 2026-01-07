# 严格提交策略（OpenCode / Husky / pre-commit）

> 目标：以后所有提交都必须经过“最严格”检查，并且由 OpenCode 自动执行提交流程
> 关键点：**不要**在 Git hook 里自动执行 `git commit`（会递归、历史污染、难回滚），而是用“严格 gate + 一键提交包装器（wrapper）”来实现“自动提交”的体验

---

## 0. 现状扫描（已确认）

### Git hooks 实际入口
- `.git/config` 设置了 `core.hooksPath = .husky/_`，所以 Git 真正执行的是 Husky 的 hook

### 当前存在的 hook
- `/.husky/pre-commit`：
  - 后端：`cd solacore-api && poetry run pre-commit run --all-files || exit 1`（严格）
  - Web：`cd solacore-web && npx lint-staged || true`（**忽略失败**）
  - Mobile：`cd solacore-mobile && npx lint-staged || true`（**忽略失败**）
- 未发现 `/.husky/commit-msg`、`/.husky/pre-push`

### 后端 pre-commit 框架
- `solacore-api/.pre-commit-config.yaml` 已定义：
  - `commit-msg-format`（调用 `solacore-api/scripts/check-commit-msg.py`）
  - `pytest-coverage`（pre-push 阶段：pytest + 覆盖率 >=85%）
- 但由于 repo 用 Husky 的 hooksPath，**仅仅跑 `./solacore-api/scripts/setup-hooks.sh` 很可能不会生效**（它安装到 `.git/hooks/*`）

---

## 1. 最严格策略（推荐的“可用 + 严格”平衡）

### 原则
1. **Hook 只做 Gate（阻止坏提交/坏 push）**，不自动产生新的 commit
2. “自动提交”由 OpenCode 运行一个 wrapper 完成：`format/lint → tests → commit-msg 校验 → git commit`
3. 分层执行（避免每次 commit 都跑 5 分钟）：
   - `pre-commit`：快（格式化/静态检查），目标 < 10-30s（严格但可忍）
   - `commit-msg`：瞬间（消息格式）
   - `pre-push`：慢（pytest+coverage / tsc / build），目标 < 1-3min
   - CI：最慢（全量）

### 你要的“最严格”定义（建议采用）
- **Commit 之前**必须满足：
  - backend: `pre-commit`（ruff/isort/mypy）
  - web/mobile: `lint-staged` 不允许失败
  - commit message 必须符合 `type(scope): subject`（conventional）
- **Push 之前**必须满足：
  - backend: pytest + coverage >=85%
  - web: `npx tsc --noEmit` + `npm run build`（可选，严格模式建议开）
  - mobile: `npx tsc --noEmit`（可选）

> 备注：你现在的 root `.husky/pre-commit` 对 web/mobile 使用了 `|| true`，这与“最严格”冲突，必须改

---

## 2. 为什么不能“在 hook 里自动 commit”

这是行业最佳实践共识（也与你现有后端 pre-commit 设计一致）：
- **递归风险**：hook 中运行 `git commit` 会再次触发 hook（无限循环或产生空提交）
- **历史污染**：自动 commit 会把格式化/修复悄悄塞进历史，你不一定 review 到最终内容
- **部分状态风险**：hook 中断可能造成半 staging、半 working tree，难以恢复

所以正确做法是：
- hook 负责“拦住不合规”
- OpenCode 负责“按步骤自动执行 + 最后 commit”

---

## 3. 需要新增/修改的 hook 文件（不在本计划中直接实施）

### 3.1 修改 `/.husky/pre-commit`
**目标：**
- 取消 `|| true`，Web/Mobile 检查失败必须阻止 commit
- 可选：仅当 staged 文件命中对应目录时才运行（避免无关项目被拖慢）

**建议逻辑：**
- 取 staged 文件列表：`git diff --cached --name-only`
- 若包含 `solacore-api/` 相关改动：运行 backend pre-commit
- 若包含 `solacore-web/`：运行 web lint-staged
- 若包含 `solacore-mobile/`：运行 mobile lint-staged

### 3.2 新增 `/.husky/commit-msg`
**目标：** commit message 强制规范
- 直接复用后端脚本：`python solacore-api/scripts/check-commit-msg.py "$1"`

### 3.3 新增 `/.husky/pre-push`
**目标：** push 前强制跑测试
- backend：`cd solacore-api && poetry run pytest -q --maxfail=1 --disable-warnings --cov=app --cov-fail-under=85`
- web（严格模式建议开）：`cd solacore-web && npx tsc --noEmit && npm run build`
- mobile（严格模式建议开）：`cd solacore-mobile && npx tsc --noEmit`

### 3.4 统一 hook 安装/启用
- 由于 `.git/config` 使用了 Husky hooksPath，确保：
  - repo root `package.json` 已有 `prepare: husky`
  - 所有 hook 文件都在 `/.husky/` 目录
- 后端 `solacore-api/scripts/setup-hooks.sh` 仍可保留作为后端开发者说明，但不应被当成唯一入口

---

## 4. OpenCode “自动提交”最佳实践（推荐实现）

### 4.1 新增一个 wrapper（比如 `scripts/strict-commit.sh`）
**职责：**
1) 运行和 hooks 一致的检查（保证可预测）
2) 生成/校验 commit message
3) 仅当全部通过后才执行 `git commit`

> 注意：wrapper 在 hook 之外执行，所以不会递归

### 4.2 OpenCode 工作流
- OpenCode 每次完成任务后：
  - 自动跑 `scripts/strict-commit.sh -m "fix(api): ..."`
  - 若失败，直接把失败原因和下一步动作用中文告诉你

---

## 5. 严格提交执行手册（你不懂也能照做）

### 常规提交（推荐）
1. `git status` 看有哪些文件改动
2. `git add -A`
3. 运行一键提交（以后让 OpenCode 执行）：
   - `scripts/strict-commit.sh -m "fix(api): align mobile auth tokens"`

### 如果 hook 阻止提交
- 说明有检查没过：
  - 按提示修复（或让 OpenCode 修复）
  - 重新 `git add -A`
  - 再次运行一键提交

### 严禁习惯性绕过
- 不要用 `git commit --no-verify`（等于关掉安全带）

---

## 6. 需要你确认的 3 个开关（决定“严格程度”）

1) `pre-commit` 阶段后端是否继续 `--all-files`
- A. 是（最严格，但可能慢）
- B. 否（只对 staged 文件，快很多）

2) `pre-push` 阶段 web 是否强制 `npm run build`
- A. 是（最严格）
- B. 否（只跑 `lint-staged` + `tsc`）

3) Mobile 是否在 `pre-push` 强制 `tsc`
- A. 是
- B. 否

---

## 7. 下一步（实施由 /start-work 执行）

当你回复这 3 个开关选项（如：`1A 2A 3A`），我会把“实施清单”固化成可执行步骤：
- 具体要改哪些文件
- 每个 hook 的最终脚本内容
- 验证命令（怎么确认 hook 真生效）
- 回滚方案
