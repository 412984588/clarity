# Claude Code 全局规范对齐：Git 自动化（Strict + 你少管事）落地计划

> 你要的结果：你不需要懂 Git / 不需要记命令。
> 你只要在聊天里说需求（例如“修复登录”），执行器会：写代码 → 跑测试 → 自动提交 → 自动推送 → 自动更新 `docs/PROGRESS.md`。
>
> 本文件是“照抄清单”，交付给执行器按步骤落地

---

## 0. 先对齐 2 个事实（不然会“你以为自动，其实没生效”）

1) 本仓库真实 hook 入口是 Husky
- 证据：`.git/config` 里 `hooksPath = .husky/_`
- 结论：**必须在 `.husky/` 下实现所有 hooks**，`.git/hooks/*` 不可靠

2) Claude Code 全局规范（你说“照抄”）对 Git 的核心要求
- 见 `~/.claude/rules/00-iron-protocol.md`、`~/.claude/rules/02-coding-standards.md`、`~/.claude/rules/03-workflow.md`
- 关键点：
  - ✅ 测试必须过
  - ✅ commit message 必须符合规范（Conventional Commits + 状态标记）
  - ✅ 自动推送（在测试全通过前不推）
  - ✅ 更新 `docs/PROGRESS.md` 记录成果

---

## 1. 目标状态（你“只想依赖我”需要的最终体验）

### 1.1 你真正需要做的事情（最少）
- 你只需要在聊天里说："做 X" 或 "修复 Y"

### 1.2 系统自动完成的链条（严格）
1) 执行器实现代码
2) 执行器跑对应测试/静态检查（必须全绿）
3) 执行器 `git add -A && git commit -m "... (Pass Test)"`
4) Husky hooks 自动触发：
- `pre-commit`：快检查 + 安全检查（失败阻止 commit）
- `commit-msg`：强制 commit message 格式（失败阻止 commit）
- `post-commit`：自动 push（会触发 `pre-push`）+ 更新 `docs/PROGRESS.md` 并二次提交 + 再 push
- `pre-push`：重检查（失败阻止 push）
5) GitHub Actions：远程再兜底（backend + web + mobile）

---

## 2. 当前仓库现状（执行器必须先确认）

### 2.1 已存在且应保留
- `.husky/pre-commit`：已按 staged 目录选择性跑 api/web/mobile
- `.husky/commit-msg`：已复用 `solacore-api/scripts/check-commit-msg.py`
- `.husky/pre-push`：已做 api 覆盖率 gate + web typecheck/lint + mobile lint
- `docs/GIT-AUTOMATION-SPEC.md`：你给的规范文档（来源于你和 claude code 对话）

### 2.2 需要补齐/修正
- 新增 `.husky/post-commit`（实现“自动 push + PROGRESS 记录”）
- 修复 `.github/workflows/mobile.yml`：当前仍指向 `clarity-mobile`（实际目录是 `solacore-mobile`）
- 新增 `.github/workflows/web.yml`（或合并进统一 `ci.yml`）：对 `solacore-web` 做 lint/tsc/build

---

## 3. 设计原则（严格 + 不让你背锅）

### 3.1 自动 push 的行业风险（你说不懂风险，我替你兜底）
- 行业普遍不建议 `post-commit` 自动 push（容易把不该公开的东西推上去）
- 但你明确要求“尽量少管事 + 自动化”，所以这里照做

### 3.2 必须加的安全护栏（不加会死循环/污染历史）
- 递归保护：使用环境变量，例如 `OPENCODE_POST_COMMIT=1`
- 只有当 remote 存在且分支可用时才 push
- 正在 merge/rebase 时跳过 PROGRESS 自动提交
- push 失败必须明确输出并退出（不能静默成功）

### 3.3 “严格测试必须过”的实现方式
- `post-commit` 的自动 push 会触发 `pre-push`
- `pre-push` 里跑重测试（失败则 push 失败，远端不会收到）

---

## 4. 执行清单（实现者照抄）

> 注意：这里是**实现步骤**，但我当前处于 planner-only 模式，本文件只负责把步骤写清楚

### 4.1 强化 commit message 规则（对齐全局规范）

现状：`solacore-api/scripts/check-commit-msg.py` 只要求 `type(scope): subject`

目标：必须附带状态标记
- 允许：`(Pass Test)` / `(No Test)` / `(Coverage XX%)`
- 示例：`fix(api): align mobile auth tokens (Pass Test)`

实现动作：
- 更新 `solacore-api/scripts/check-commit-msg.py`：正则允许上述尾缀
- 确保 `.husky/commit-msg` 继续调用该脚本

### 4.2 新增 Husky `post-commit`

新增文件：
- `.husky/post-commit`
- `.husky/_/post-commit`（两行路由壳）

`.husky/post-commit` 行为：
1) 防递归
- 若 `OPENCODE_POST_COMMIT=1` → 直接退出 0

2) 获取当前分支
- `BRANCH=$(git branch --show-current)`
- 若空/Detached HEAD → 输出并退出 0

3) 自动 push（触发 pre-push 测试）
- 若无 `origin` → 输出并退出 0
- 先 `git push origin "$BRANCH"`
- 失败再 `git push -u origin "$BRANCH"`
- 若仍失败 → 输出并退出 1

4) 更新 `docs/PROGRESS.md`
- 若文件不存在 → 输出并退出 0（不阻塞主流程）
- 生成条目并插入第一个 `---` 之后
- `git add docs/PROGRESS.md`

5) 记录 PROGRESS（不改写历史，避免 force push）
- 新建一个 commit（推荐）：`docs(progress): auto update (Pass Test)`
- 关键：该 commit 需要带 `OPENCODE_POST_COMMIT=1` 环境变量，避免再次触发 post-commit 递归

6) 再 push
- `git push origin "$BRANCH"`

> 说明：规范文档里写了 amend + force-with-lease，但你之前表达过“不想 force、不想 amend”，所以这里用“新 commit”方案，依然满足“自动更新 PROGRESS + 自动推送”，且更安全

### 4.3 修正/补齐 GitHub Actions（远程兜底）

1) 修复 `.github/workflows/mobile.yml`
- `working-directory: solacore-mobile`
- `cache-dependency-path: solacore-mobile/package-lock.json`

2) 新增 `.github/workflows/web.yml`
- 工作目录：`solacore-web`
- Steps：`npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`

3) 保留 `.github/workflows/backend.yml`（已可用）

---

## 5. 验证计划（必须给你“证据”，不靠嘴说）

### 5.1 Objective
验证：commit → hooks → push → CI 全链路严格工作

### 5.2 Test Cases
1) `commit-msg` 拦截
- 使用不合规 message，必须失败

2) `pre-commit` 拦截
- staged 文件包含 `<<<<<<<`，必须失败

3) `post-commit` 自动化
- 提交一次合规 commit：
  - 自动 push（会触发 pre-push）
  - `docs/PROGRESS.md` 出现新条目
  - 自动产生第二个 commit（docs(progress)）并 push

4) `pre-push` 闸门
- 故意让测试失败 → push 必须失败

5) GitHub Actions
- push 后在 GitHub Actions 里看到 backend/web/mobile workflow 运行

---

## 6. 回滚方案（出问题 1 分钟恢复）

- 删除 `.husky/post-commit` 与 `.husky/_/post-commit`
- 回退 `.github/workflows/mobile.yml` 和新增的 web workflow
- commit-msg 校验恢复到旧正则

---

## 7. 你现在只需要做的事（最少）

你已经说“允许”，我会把这份计划交给执行器落地
- 你不需要记任何命令
- 你只要继续像现在这样：用中文说需求即可
