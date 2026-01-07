# Git 自动化工作流落地计划（对齐 GIT-AUTOMATION-SPEC.md）

> 角色声明：本文件是交付给执行器的“照抄清单”。执行时严格按本文件修改、跑验证、输出证据。

## 0. 目标（你期望的体验）

你不想学也不想管 Git/测试/推送：
- 你只需要提出需求（或在本地改完后做一次 `git commit`）
- 系统自动完成：格式化/安全检查/拦截不合规提交/跑测试/推送到 GitHub/更新 `docs/PROGRESS.md`

## 1. 成功标准（Pass/Fail，必须可验证）

### 功能性
1. `git commit -m "feat(api): ..."` 会自动触发：
   - 后端/前端/移动端各自的格式化 + lint（只在对应子项目变更时）
   - commit message 不合规会被拒绝
2. commit 成功后自动：
   - push 到 `origin/<当前分支>`（普通 push，禁止 force push）
   - 追加一条 `docs/PROGRESS.md` 记录（以“新 commit”的方式，不用 amend，不重写历史）
3. `git push` 前自动触发：
   - 后端：pytest + coverage gate（`--cov-fail-under=85`）
   - web：`tsc --noEmit` + `npm run lint`（若该目录有变更）
   - mobile：`npm run lint`（若该目录有变更；可选加 tsc）

### 可观察
- 终端输出能看见 hook 执行步骤（中文提示为主）
- 测试失败会明确阻断 push（exit code != 0）
- `git log -5` 能看到：业务 commit + `docs(progress): ...` 进度 commit

### 二进制判定
- 任何 hook 步骤失败：commit/push 必须失败（不允许 `|| true` 吞错）
- 不允许 `--force`, `--force-with-lease`, `git commit --amend`
- 不允许 hook 递归触发无限循环

## 2. 当前仓库现状（已确认）

### 2.1 Hook 入口
- `.git/config` 已设置：`core.hooksPath = .husky/_`
- 结论：**必须把所有 hook 规则统一放在 `.husky/`**，`.git/hooks/*` 不可靠

### 2.2 已存在的 hooks
- 已有：`.husky/pre-commit`（按 staged 变更选择性跑 api/web/mobile）
- 已新增但未确认是否已纳入版本控制：`.husky/commit-msg`、`.husky/pre-push`

### 2.3 CI 现状
- backend CI 正常：`.github/workflows/backend.yml`
- mobile CI 路径疑似不对：`.github/workflows/mobile.yml` 仍指向 `clarity-mobile`
- web CI 不完整/缺失

## 3. 落地方案（严格版，尽量少让你操心）

### 3.1 本地 hooks（唯一入口：Husky）

#### A) `commit-msg`（强制 Conventional Commit）
- 文件：`.husky/commit-msg`
- 行为：调用 `solacore-api/scripts/check-commit-msg.py "$1"`
- 失败：阻断 commit

#### B) `pre-commit`（快、严格、按变更目录触发）
- 文件：`.husky/pre-commit`
- 行为（按 staged 变更目录）：
  - `solacore-api/**`：`poetry run pre-commit run`（不使用 `--all-files`）
  - `solacore-web/**`：`npx lint-staged`
  - `solacore-mobile/**`：`npx lint-staged`
- 失败：阻断 commit

> 注意：这部分要对齐 spec 里的“安全检查（合并冲突/大文件/私钥）”。
> 具体实现：
> - 后端：已在 `solacore-api/.pre-commit-config.yaml` 覆盖大部分（trailing whitespace、detect private key、large files等）
> - web/mobile：靠 `lint-staged + prettier/eslint`，如要“私钥/大文件/merge-conflict”也覆盖，需要在根或子项目补充（见 4.2）

#### C) `post-commit`（自动 push + 自动写 PROGRESS.md）
- 文件：建议新增 `.husky/post-commit`（或等价挂载在 Husky 支持的 hook）
- 行为：
  1) 防递归：检测环境变量（例如 `AUTO_PROGRESS_COMMIT=1`）时跳过
  2) push：普通 push（不 force）
     - 若未设置 upstream：`git push -u origin <branch>`
  3) 更新 `docs/PROGRESS.md`：
     - 生成记录块（时间戳 + commit message + 测试/推送状态）
     - `git add docs/PROGRESS.md`
     - `git commit -m "docs(progress): record <short message>"`（新 commit，不 amend）
     - 再次 push（普通 push）

> 关键要求：
> - **禁止**：`--force-with-lease`、`git commit --amend`
> - **必须**：可重复运行且不会无限循环

#### D) `pre-push`（重校验，阻断 push）
- 文件：`.husky/pre-push`
- 行为（按 diff 范围 `origin/main...HEAD` 判断受影响子项目）：
  - api：pytest + coverage gate
  - web：`npx tsc --noEmit` + `npm run lint`
  - mobile：`npm run lint`（可选：`npx tsc --noEmit`，如果移动端已配置好）
- 失败：阻断 push

### 3.2 CI（GitHub Actions）

目标：本地绕过也能在远程拦截。

#### A) 修正 Mobile CI 路径
- 修改：`.github/workflows/mobile.yml`
- 把 `working-directory: clarity-mobile` 改为 `solacore-mobile`
- 把 `cache-dependency-path` 指向 `solacore-mobile/package-lock.json`（如果存在）

#### B) 新增 Web CI
- 新增：`.github/workflows/web.yml`
- 内容：`npm ci`（在 `solacore-web`）、`npm run lint`、`npx tsc --noEmit`、`npm run build`

#### C) 新增统一 `ci.yml`（对齐 spec）
- 新增：`.github/workflows/ci.yml`
- 做两件事：
  1) Node 侧：prettier check + test/build（仅当有脚本）
  2) Python 侧：`pre-commit run --all-files`（在 `solacore-api` 或根目录按策略）

> 注意：当前仓库已存在 `backend.yml`，可以保留或合并。

## 4. 执行清单（给实现者照抄）

### 4.1 文件变更列表（必须）
1. 确保以下文件存在且已纳入 git：
   - `.husky/commit-msg`
   - `.husky/pre-commit`
   - `.husky/pre-push`
   - `.husky/post-commit`（新增）
2. 更新/新增 GitHub Actions：
   - 更新 `.github/workflows/mobile.yml`（修 working-directory）
   - 新增 `.github/workflows/web.yml`
   - 新增 `.github/workflows/ci.yml`

### 4.2 对齐 spec 的“安全检查”覆盖面（建议，但你想最严格就必须做）
- 方案 1（推荐）：在仓库根新增 `.pre-commit-config.yaml`，覆盖通用安全检查（merge-conflict/私钥/大文件/yaml/json 等），并通过 `.husky/pre-commit` 调用 `pre-commit run`
- 方案 2（折中）：保持后端用 python pre-commit；web/mobile 用 npm lint-staged；再在 `.husky/pre-commit` 前增加 3 个轻量检查：
  - grep merge-conflict
  - 检查大文件
  - 检测私钥（可用 `gitleaks`，但会引入依赖）

## 5. 验证步骤与证据（必须输出）

1) 本地验证（演练一次 commit）：
- 准备一个最小改动（例如改一个 README 行）
- 运行 commit（执行器负责），观察：pre-commit 跑、commit-msg 校验

2) 验证 post-commit：
- commit 成功后自动 push
- 自动生成 `docs(progress): ...` 新 commit
- 证明无递归：日志只出现一次进度 commit，不会无限追加

3) 验证 pre-push：
- 在 api/web/mobile 分别做一次最小改动
- push 时对应检查会触发（失败会阻断）

4) CI 验证：
- 推送到 GitHub 后，Actions 中能看到 backend/web/mobile/ci 任务按预期运行

## 6. 回滚方案（最坏情况一键撤回）

- 删除/回退这些文件：`.husky/post-commit`、`.husky/pre-push`、`.husky/commit-msg`
- 恢复 `.husky/pre-commit` 到旧版本
- CI：回退新增 workflows

---

## 7. 给非程序员的解释（你只需要知道这 2 句话）

- “commit”= 保存一次改动的快照
- “push”= 把本地保存的改动上传到 GitHub（远程仓库）
