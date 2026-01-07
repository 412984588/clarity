# Git 自动化工作流落地方案（按 GIT-AUTOMATION-SPEC.md 适配本仓库）

> 目标：实现你给的 `GIT-AUTOMATION-SPEC.md` 那套“你尽量少管、严格规范、自动推送、自动更新 PROGRESS.md、CI 再兜底”的全自动流程
> 
> 注意：本仓库当前 **实际生效的 Git Hooks 入口是 Husky**（`.git/config` 里 `core.hooksPath = .husky/_`）。因此规范文档里写的 `.git/hooks/*` 需要 **改成 Husky 版本** 才会真正执行。

---

## 0. 你问的“push”是什么意思（1 句话）

- `git push` = 把你本地的提交上传到 GitHub 远程仓库

---

## 1. 我已调查到的“当前真实现状”（事实清单）

### 1.1 Hook 实际入口
- `/.git/config` 已设置：`core.hooksPath = .husky/_`
- 结论：Git 不会走默认 `.git/hooks/*`（除非取消 hooksPath）

### 1.2 现有 Hook 行为
- 已存在并生效：`/.husky/pre-commit`
  - staged 改动包含 `solacore-api/**` 时：`cd solacore-api && poetry run pre-commit run`
  - staged 改动包含 `solacore-web/**` 时：`cd solacore-web && npx lint-staged`
  - staged 改动包含 `solacore-mobile/**` 时：`cd solacore-mobile && npx lint-staged`
- 但当前 repo 状态里：
  - `.husky/commit-msg`、`.husky/pre-push` 不是稳定存在（曾被识别为 untracked）
  - 这意味着：提交信息规范、推送前测试可能 **并没有强制执行**

### 1.3 后端已有 pre-commit 配置
- `solacore-api/.pre-commit-config.yaml` 已定义：
  - `commit-msg` 检查：`python scripts/check-commit-msg.py`
  - `pre-push` 测试+覆盖率门槛：`pytest ... --cov-fail-under=85`
- 但：只靠 `pre-commit install` 写入 `.git/hooks/*` 的方式，在 Husky hooksPath 模式下 **可能不会生效**

### 1.4 CI 现状
- 后端 CI 真实在跑：`.github/workflows/backend.yml`
- 但 repo 中存在多份疑似“旧路径 clarity-*”的 workflow（可能不生效/不覆盖 web/mobile）

---

## 2. 你要的“规范文档流程”在本仓库的正确实现方式

规范文档里的流程：
- `git commit` → pre-commit（格式化/安全检查/提醒）
- commit 成功 → post-commit（自动 push + 更新 PROGRESS.md + 同步）
- `git push` → pre-push（跑测试，不通过禁止 push）
- push 到 GitHub → GitHub Actions（强制全量检查）

在本仓库的正确落地点：
- 用 Husky 统一实现 `pre-commit`/`commit-msg`/`pre-push`/`post-commit`
- GitHub Actions 用 monorepo 方式补齐 web/mobile

---

## 3. 成功标准（可验证、可观测、二值化）

### 3.1 功能标准
1. 执行 `git commit -m "feat(api): xxx"` 时：
   - 会自动跑 pre-commit 检查
   - 任何检查失败 → commit 被阻止
2. commit 成功后：
   - 自动 `git push` 到 `origin/<当前分支>`
   - 自动更新 `docs/PROGRESS.md`
3. 执行 `git push` 前：
   - 会自动跑对应项目测试/检查
   - 失败 → push 被阻止
4. push 到 GitHub 后：
   - GitHub Actions 会跑完对应检查（后端/前端/移动端/安全检查）

### 3.2 可观测标准（你能看到）
- commit 时终端明确打印：正在跑哪些检查、失败原因、下一步该怎么做
- post-commit 明确打印：push 成功/失败
- PROGRESS.md 顶部出现一段带时间戳的记录

### 3.3 Pass/Fail 标准
- 任意检查失败：commit/push 必须直接失败（退出码非 0）

---

## 4. 需要落地的文件清单（实现者照抄）

### 4.1 Husky hooks（关键）
- `/.husky/pre-commit`（改）
- `/.husky/commit-msg`（新增）
- `/.husky/pre-push`（新增）
- `/.husky/post-commit`（新增）

> 说明：由于 `core.hooksPath=.husky/_`，这些文件将由 Husky 机制执行

### 4.2 GitHub Actions（关键）
- `/.github/workflows/ci.yml`（新增：全量 CI 主入口）
- 评估并处理“旧 clarity-* workflow”：
  - `/.github/workflows/api.yml`
  - `/.github/workflows/deploy.yml`
  - `/.github/workflows/mobile.yml`

### 4.3 复用或新增脚本（可选，但建议）
- 复用：`solacore-api/scripts/check-commit-msg.py`
- 可新增：`scripts/git/show-diff-reminder.sh`（用于 pre-commit 提醒）

---

## 5. 具体实现步骤（严格按你的规范文档）

> 这是给“实现者/执行者”的逐步落地清单，你不需要理解代码；照做即可

### Step 1：统一 hook 系统入口（确认 Husky 为唯一入口）
- 确认 `.git/config` 里 `core.hooksPath = .husky/_` 保持不变
- 不再依赖 `solacore-api/scripts/setup-hooks.sh` 写入 `.git/hooks/*`
  - 方案：更新该脚本/文档，改为“提示用户用根目录 Husky hooks”

### Step 2：实现 `commit-msg`（Conventional Commit 强制）
- 新增 `/.husky/commit-msg`
- 内容：调用 `python3 solacore-api/scripts/check-commit-msg.py "$1"`
- 验证：
  - `git commit -m "bad message"` 必须被拒绝
  - `git commit -m "fix(api): ok"` 必须通过（只看消息格式）

### Step 3：实现 `pre-commit`（按规范文档的“快检查”）
- 修改现有 `/.husky/pre-commit`
- 要求（对应规范文档）：
  - 删除行尾空格、文件末尾换行、yaml/json 校验、合并冲突检查、大文件、私钥检查
  - `show-git-diff` 提醒
  - Web/Mobile：Prettier + markdownlint（通过 lint-staged 或 pre-commit tools）

> 重要：你给的规范文档把这些都放在 `.pre-commit-config.yaml`（Python pre-commit 框架）
> 但本仓库已有 “web/mobile 用 lint-staged” 的模式，所以建议：
> - `solacore-api`：继续使用 Python `pre-commit`（ruff/isort/mypy + 基础安全）
> - `solacore-web`/`solacore-mobile`：继续用 `lint-staged`（Prettier/ESLint 等）
> - 根目录再补一层“通用检查”（可用 Python pre-commit 或用轻量脚本）

严格要求：
- 任何子项目检查失败 → `pre-commit` 必须退出非 0，阻止 commit

### Step 4：实现 `post-commit`（自动 push + 更新 PROGRESS.md）
- 新增 `/.husky/post-commit`
- 行为按你文档：
  1) 自动推送 `git push origin <当前分支>`；首次推送用 `-u`
  2) 更新 `docs/PROGRESS.md` 顶部插入记录（时间戳 + commit message + 测试通过/推送完成）
  3) 自动 `git commit --amend --no-edit` 把 PROGRESS.md 纳入同一个 commit
  4) `git push --force-with-lease` 推送 amend 后的新 commit

> 注：这里与“业界最佳实践”有冲突（amend + force push 风险），但你明确要求“就按这个做”，所以计划按此实现

### Step 5：实现 `pre-push`（严格测试闸门）
- 新增 `/.husky/pre-push`
- 按你的“最严格”要求（你回答了 A）：
  - `solacore-api`：跑 pytest + 覆盖率门槛（复用现有 `--cov-fail-under=85`）
  - `solacore-web`：跑 `npx tsc --noEmit` + `npm run lint` +（可选）`npm run build`
  - `solacore-mobile`：跑 `npx tsc --noEmit` + `npm run lint`

### Step 6：GitHub Actions `ci.yml`（最终兜底）
- 新增 `/.github/workflows/ci.yml`
- 触发：push/PR 到 main
- jobs（建议分 3 个目录并行）：
  - `backend`：按 `.github/workflows/backend.yml` 的方式（或直接复用/合并）
  - `web`：`npm ci` + `npm run lint` + `npx tsc --noEmit` + `npm run build`
  - `mobile`：`npm ci` + `npm run lint` + `npx tsc --noEmit`
- 另外增加一个 job：跑 `pre-commit run --all-files`（如果你想完全复刻规范文档）

---

## 6. 你要“你尽量少管”的最终体验（验收口径）

当上述落地完成后，你日常只需要：
- 你跟我说需求（我写代码/跑测试/提交）
- 我执行 `git commit` 后，hook 会自动：
  - 格式化 + 安全检查
  - commit-msg 规范
  - 自动 push
  - 自动更新 `docs/PROGRESS.md`

你不需要学 Git，也不需要记复杂流程

---

## 7. 回滚方案（万一你不喜欢）

- 删除：`/.husky/post-commit`（立刻停止自动 push/自动改 PROGRESS）
- 删除：`/.husky/pre-push`（立刻停止 push 前强制测试）
- 保留：`/.husky/pre-commit`、`/.husky/commit-msg`（保留基本质量/提交规范）

---

## 8. 下一步（执行入口）

我现在是 planner，已经把“按你文档落地”的可执行清单写完整了。

如果你要我真正去修改仓库文件并验证生效：请运行 `/start-work`（或切换到允许实现的模式）。
