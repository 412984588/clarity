# Git 自动化工作流（按 GIT-AUTOMATION-SPEC.md）落地执行计划

> 目标：让你“几乎不用管”，日常只需要 **提交一次**（或更进一步：只说需求，我来写代码并自动提交/推送）。
> 
> 约束：本仓库当前真实 hook 入口是 Husky（`.git/config: core.hooksPath = .husky/_`）。因此 **不能按文档写到 `.git/hooks/*`**，否则不会触发。需要把等价逻辑实现到 `.husky/*`。

---

## 0. 你问的「push」是什么意思（1 句话）

- `push` = 把你电脑上的提交 **上传到 GitHub 远程仓库**

---

## 1. 当前仓库现状（已核对）

### 1.1 Git 实际使用的 hooks

- `core.hooksPath = .husky/_`（真实生效）
- 这意味着：Git 只会执行 `.husky/_/<hook>`（再由 Husky 转发到 `.husky/<hook>`）

### 1.2 当前已存在并会运行的 hook

- 已存在：`.husky/pre-commit`（会运行）
  - 如果本次 commit 有改到：
    - `solacore-api/**`：跑 `poetry run pre-commit run`
    - `solacore-web/**`：跑 `npx lint-staged`
    - `solacore-mobile/**`：跑 `npx lint-staged`

### 1.3 当前缺口（导致“不是全自动/不够严格”的点）

- 缺少 **post-commit**：commit 成功后自动推送、自动更新 `docs/PROGRESS.md`
- `.github/workflows`：mobile 的 CI workflow 仍指向 `clarity-mobile`（路径漂移），web 的 CI 未完整覆盖
- 规范里的“通用安全检查”（merge conflict / private key / large file / yaml/json）目前 **没有统一在 monorepo 层做全覆盖**

---

## 2. 你要求的“完全照抄 spec”的执行矩阵（严格版）

> 你选择了 A（最严格），这里按“最严格”计划执行

### 2.1 `git commit` 时（pre-commit）必须做

- 安全/卫生检查（强制阻止提交）：
  - trailing whitespace
  - end-of-file newline
  - YAML/JSON 格式
  - merge conflict marker
  - detect private key
  - block large files (>500KB)
  - 提醒看 `git diff --cached`
- 格式化（强制）：
  - web/mobile：`lint-staged`（已有）
  - backend：`pre-commit`（已有）

### 2.2 `git commit` 成功后（post-commit）必须做

- 自动推送到 `origin/<当前分支>`
- 更新 `docs/PROGRESS.md`（插入记录）
- amend 本次 commit（把 PROGRESS.md 也放进同一个 commit）
- 强制 push（`--force-with-lease`）保证 amend 后能同步到远程

> 注意：这一步是你 spec 里的核心“全自动”。实现时必须加 **防递归锁**，否则 post-commit 里再 `git commit --amend` 会再次触发 post-commit 无限循环。

### 2.3 `git push` 前（pre-push）必须做

- 按变更范围跑更重的测试（失败阻止 push）：
  - `solacore-api`：pytest + coverage gate（已有配置，落地到 Husky）
  - `solacore-web`：`npx tsc --noEmit` + `npm run lint` +（严格版可加 `npm run build`）
  - `solacore-mobile`：`npx tsc --noEmit`（若可用）+ `npm run lint`

### 2.4 Push/PR 后（GitHub Actions）必须做

- 后端：已有 `backend.yml`，但 coverage gate/全量 pre-commit 需要对齐
- web：新增或补齐 workflow：lint + tsc + build
- mobile：修正 workflow 路径（`clarity-mobile` -> `solacore-mobile`）并跑 lint + tsc

---

## 3. 具体落地改动（实现者照抄清单）

### 3.1 Husky hooks（这是最关键）

#### A) 新增 `.husky/post-commit`（等价替代 `.git/hooks/post-commit`）

必须包含：
- 防递归锁（环境变量/lockfile 任一）
- 只在存在 `origin` 时 push
- 更新 `docs/PROGRESS.md`：插入到第一个 `---` 之后
- `git add docs/PROGRESS.md`
- `git commit --amend --no-edit --no-verify`
- `git push --force-with-lease`

同时检查 `.husky/_/post-commit` 是否存在：
- 若不存在：新增一个 2 行转发脚本（与 `.husky/_/commit-msg` / `.husky/_/pre-push` 同风格）

#### B) 补齐 `.husky/pre-push`（你现在 repo 里已生成过模板，但要确认是否已被 git 跟踪）

- 迁移你 `solacore-api/.pre-commit-config.yaml` 里的 `pytest-coverage` gate 到 Husky pre-push
- web/mobile 增加 tsc/lint/build（严格版按 A）

#### C) 强制 commit message（`.husky/commit-msg`）

- 复用 `solacore-api/scripts/check-commit-msg.py "$1"`

> 这一步能保证你以后 commit message 永远符合规范（不需要你理解规范，只要照模板填）

#### D) 扩展 `.husky/pre-commit` 的“通用安全检查”

- 方案 1（推荐，最贴近 spec）：在根目录引入 `pre-commit` 框架的通用 hooks（需要新增 root `.pre-commit-config.yaml`）
- 方案 2（更轻依赖）：直接在 `.husky/pre-commit` 里用 shell 实现上述检查

> 选择 A（最严格）：方案 1 + 方案 2 组合也可以（但不建议重复跑同类检查）

---

## 4. 一次性安装/配置（为了“以后不用管”）

> 你说“我不想运行命令/不想记命令”，所以这里的目标是：**一次性由执行器帮你配置好**。

执行器需要确保：
- 本地已装：Node/NPM（用于 husky/lint-staged）
- 后端已装：Poetry + Python（用于 backend pre-commit/pytest）
- Husky 已安装：根目录 `package.json` 有 `prepare: husky`（已存在）

---

## 5. 验证与证据（必须输出）

实现完成后，必须提供以下“证据输出”（你无需看懂，但我会给你截图/日志）：

1) `git commit` 触发：
- 预期：能看到 pre-commit 执行日志；任意检查失败 => commit 失败

2) `git commit` 成功后：
- 预期：自动 push 的日志
- 预期：`docs/PROGRESS.md` 顶部新增记录
- 预期：远程分支可见本次 commit（含 PROGRESS 更新）

3) `git push` 前：
- 预期：pre-push 运行测试/类型检查；失败 => push 被拦截

4) GitHub Actions：
- 预期：backend/web/mobile workflow 都能跑

---

## 6. 最小化你参与的“操作模型”

你以后只需要：
- 说需求（比如“把 hooks 按 spec 配好”）
- 或者（如果你自己会用 git）：`git commit -m "..."`

其余：
- 我（执行器）负责写代码、跑测试、自动提交、自动推送、更新进度

---

## 7. 风险声明（不要求你懂，只用于决策记录）

你提供的 spec 里包含：post-commit 自动 amend + force-with-lease。
- 这是**非主流**做法，风险是：提交历史会频繁被改写；一旦协作多人，可能引发冲突。
- 但你明确要求“照 spec 做 + 你不想管 + 最严格”，所以方案会照做，并在实现里加防递归/失败回滚保护。
