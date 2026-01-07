# Git 自动化工作流（严格版）执行清单（交付给执行器照抄）

> 你说“我不想管，全部你完成”，目标是：
> - 你只需要**提出需求**（例如“修复登录 bug”）
> - 执行器（AI/工程师）负责：实现 → 自测 → **按规范自动提交** → **自动推送** → 记录进度
>
> 约束（本仓库事实）：`.git/config` 已设置 `core.hooksPath=.husky/_`，所以**Git 实际执行的是 Husky hooks**。
> - 任何写在 `.git/hooks/*` 的脚本在这里**不会生效**
> - 必须用 `.husky/<hook>` + `.husky/_/<hook>` 路由文件

---

## 0. 关键概念（给非程序员）

- `commit`：把本地改动“打包成一次记录”
- `push`：把本地的 commit **上传到 GitHub**（远程仓库）

你要的“全自动”，就是：我做完工作后，本地 commit 产生后，系统自动 push 到 GitHub。

---

## 1. 成功标准（必须可验证）

### 1.1 功能性（Functional，Pass/Fail）
1) `git commit` 触发 `pre-commit`：任何检查失败 → **commit 被阻止**
2) commit message 不符合 `type(scope): subject` → **commit 被阻止**
3) commit 成功后触发 `post-commit`：
   - 自动 push 到 `origin/<当前分支>`（普通 push，不强推）
   - 自动更新 `docs/PROGRESS.md`（新增一条记录）
   - 自动创建一个新的 commit（例如 `docs(progress): update progress`）并 push
   - 必须有**防递归**（否则会无限循环）
4) `git push` 触发 `pre-push`：测试/类型检查失败 → **push 被阻止**
5) GitHub Actions：push/PR 时自动跑 CI（至少覆盖 backend + web + mobile）

> 说明：你给的规范文档里写的是 `amend + force-with-lease`，但你后来确认更安全的版本：
> - ✅ 不用 `--force-with-lease`
> - ✅ 不用 `git commit --amend`
> - ✅ 改成创建新 commit
> 这会产生 2 个 commits（你的功能 commit + PROGRESS 更新 commit），是预期行为

### 1.2 可观察证据（Observable）
- 终端输出能看到：pre-commit / commit-msg / post-commit / pre-push 的执行日志
- `git show -1` 能看到 `docs/PROGRESS.md` 的新增记录（在最近一次 docs(progress) commit 中）
- GitHub Actions 页面能看到对应 workflow 运行

---

## 2. 本仓库现状（高置信度）

### 2.1 Hook 入口
- `/.git/config`：`hooksPath = .husky/_`
- Husky 分发器：`.husky/_/h`

### 2.2 已存在的 hooks（当前 repo）
- `.husky/pre-commit`：已实现（含 staged 安全扫描 + 按子项目运行）
- `.husky/commit-msg`：已实现（复用 `solacore-api/scripts/check-commit-msg.py`）
- `.husky/pre-push`：已实现（后端 pytest+cov gate、web tsc+lint、mobile lint）
- `.husky/_/post-commit`：已存在路由文件（两行壳），但**缺少 `.husky/post-commit` 真正逻辑**

### 2.3 CI 现状
- `.github/workflows/backend.yml`：存在且工作目录为 `solacore-api`（基本正确）
- `.github/workflows/mobile.yml`：存在但工作目录指向 `clarity-mobile`（需要修正为 `solacore-mobile`）
- `.github/workflows/web.yml`：未找到（需要新增）

---

## 3. 执行步骤（实现者照抄，严格按顺序）

> 重要：以下步骤是“落地实现”。如果你在另一个模式里是 planner，则把这些交给执行器去做。

### Step 3.1 新增 Husky `post-commit`

**目标**：commit 成功后自动 push + 自动更新 `docs/PROGRESS.md` + 自动再 commit + push

**新增文件**：`.husky/post-commit`

**脚本要求（必须满足）**：
- 防递归：环境变量 `OPENCODE_POST_COMMIT=1` 时直接退出 0
- 避免在 rebase/merge 时运行：检测 `.git/rebase-apply` / `.git/rebase-merge` / `.git/MERGE_HEAD`，存在则跳过（退出 0 + 打印提示）
- 自动 push（普通 push）：
  - 首先 `git push origin <branch>`
  - 失败则尝试 `git push -u origin <branch>`
- 更新 `docs/PROGRESS.md`：
  - 时间戳：`YYYY-MM-DD HH:MM`
  - 读取刚刚那个 commit 的 message：`git log -1 --pretty=%B`
  - 在 `docs/PROGRESS.md` 第一个 `---` 后插入：
    - `### [timestamp] - 自动提交`
    - `- [x] 完成: <commit message>`
    - `- [x] 推送: 完成`
    - `---`
- 生成新 commit（不 amend，不 force push）：
  - `git add docs/PROGRESS.md`
  - `OPENCODE_POST_COMMIT=1 git commit -m "docs(progress): update progress"`
  - `git push origin <branch>`（失败则提示并退出非 0）

**注意**：
- 这里不写“测试通过 ✅”，因为真实测试在 `pre-push` / CI 才是事实来源

### Step 3.2 确认 `.husky/_/post-commit` 路由文件存在

- 文件：`.husky/_/post-commit`
- 内容应与其他路由文件一致（两行）：
  - `#!/usr/bin/env sh`
  - `. "$(dirname "$0")/h"`

### Step 3.3 维持 `pre-commit` 严格（现状已满足）

- `.husky/pre-commit` 目前已做到：web/mobile 不再 `|| true`，失败会阻止 commit
- 额外建议（可选）：保持它“快”（< 3 秒），重测试留给 `pre-push`

### Step 3.4 修复/补齐 GitHub Actions

1) 修复 `.github/workflows/mobile.yml`
- `working-directory: solacore-mobile`
- `cache-dependency-path: solacore-mobile/package-lock.json`

2) 新增 `.github/workflows/web.yml`
- `working-directory: solacore-web`
- 顺序：`npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`

> 可选：新增统一 `.github/workflows/ci.yml`（把 pre-commit 全量校验也放进去）。
> 但为了最小风险，建议先把 web/mobile 修正到能跑，再考虑收敛成统一 ci。

---

## 4. 验证步骤（必须给出“证据输出”）

### 4.1 验证 hooksPath
- 证据：`git config --get core.hooksPath` 输出应为 `.husky/_`

### 4.2 验证 commit-msg gate
- 方式：尝试 `git commit -m "bad msg"`
- 期望：被阻止（脚本提示 Expected: type(scope): subject）

### 4.3 验证 post-commit 自动化
- 在临时分支上：
  - 做一个小改动并 commit
  - 期望：
    - 自动 push 成功
    - `docs/PROGRESS.md` 被更新并产生第二个 `docs(progress)` commit
    - 无无限循环

### 4.4 验证 pre-push gate
- 方式：`git push`
- 期望：自动跑测试/检查；失败则阻止 push

### 4.5 验证 CI
- 方式：push 后在 GitHub Actions 看 workflow 运行
- 期望：backend + web + mobile 都能跑到

---

## 5. 风险说明（你不用懂，但执行器必须知道）

- 业界普遍不建议 hook 自动 push / 自动改文件再提交；你要求“完全自动化”，所以必须加：
  - 防递归（环境变量）
  - rebase/merge 检测
  - 失败显式输出（不要静默失败）

---

## 6. 交付物清单（最终 repo 应该出现）

- `.husky/post-commit`
- `.github/workflows/web.yml`（新增）
- `.github/workflows/mobile.yml`（修正路径）

（已存在但应保持严格）
- `.husky/pre-commit`
- `.husky/commit-msg`
- `.husky/pre-push`
