# Git 自动化（按 GIT-AUTOMATION-SPEC.md）落地执行计划 — Ultra Strict

> 面向“我不懂编程/不想记命令”的目标：你只提需求，我负责实现、测试、提交、推送、记录。
>
> 重要前提：当前仓库 Git 配置 `core.hooksPath=.husky/_`，所以所有 hooks 必须以 Husky 作为唯一入口（`.husky/*` + `.husky/_/*`）。

## 0. 现状核对（以仓库实际为准）

- 生效入口：`.git/config` 含 `hooksPath = .husky/_`
- 已有：`.husky/pre-commit`（已做 staged 安全检查 + 子项目检查）
- 已有：`.husky/commit-msg`（调用 `solacore-api/scripts/check-commit-msg.py`）
- 已有：`.husky/pre-push`（后端 pytest+cov gate 85%，web tsc+lint，mobile lint）
- 缺口：**没有**可执行的 `.husky/post-commit`（只有 `.husky/_/post-commit` 路由文件不够）
- CI：后端 workflow 存在（`.github/workflows/backend.yml`）；mobile workflow 路径疑似旧目录（需改成 `solacore-mobile`）；web workflow 缺失

## 1. 成功标准（必须可验证）

### Functional（必须满足）
1. `git commit` 前：pre-commit 失败则阻止 commit
2. `git commit` 时：commit message 不合规则阻止 commit（Conventional Commits：`type(scope): subject`）
3. `git commit` 成功后：post-commit 自动执行
   - 自动 push 到 `origin/<当前分支>`
   - 自动更新 `docs/PROGRESS.md`
   - PROGRESS 更新要进入 Git 历史（两种策略见下）
4. `git push` 前：pre-push 自动执行
   - 后端 pytest + coverage gate（85%）失败阻止 push
   - web TypeScript 类型检查 + lint（可选 build）失败阻止 push
   - mobile lint（可选 tsc）失败阻止 push
5. push / PR 后：GitHub Actions 自动跑 CI（backend/web/mobile）

### Observable（你能看见的）
- 终端输出清晰提示每一步（pre-commit / commit-msg / post-commit / pre-push）
- `docs/PROGRESS.md` 顶部出现新纪录
- GitHub Actions 里能看到 workflow run

## 2. 关键决策：按你要求“全自动”但要避免毁仓库

你贴的 `GIT-AUTOMATION-SPEC.md` 里有两点是**行业公认高风险**：
- `post-commit` 自动 `git commit --amend`
- `post-commit` 自动 `git push --force-with-lease`

你明确说“你不懂风险，也不想管”，所以这里给两个可选落地策略：

### 策略 S（最贴近 spec，但仍需安全护栏）
- post-commit：push → 更新 `docs/PROGRESS.md` → `--amend` → `--force-with-lease`
- 必须加：递归保护（环境变量）、rebase/merge 检测、origin 不存在/网络失败处理

### 策略 B（我推荐的严格安全版，维护成本最低）
- post-commit：push → 更新 `docs/PROGRESS.md` → **新建一个 commit**（不 amend、不 force）→ 普通 push
- 优点：不会重写历史，不会强推；缺点：每次会多 1 个 progress commit（你之前也表示可接受）

> 建议默认采用策略 B。只有你明确要求“必须 100% 按 spec 的 amend+force”，才切到策略 S。

## 3. 需要执行器实现/修改的文件清单（只列必须项）

### 3.1 Husky：补齐 post-commit
- 新增：`.husky/post-commit`
- 确认：`.husky/_/post-commit`（已存在则只校验，不重复创建）

post-commit 需要做：
1. 检查 `origin` 是否存在；不存在则退出 0
2. 获取当前分支名
3. 执行普通 push（失败尝试 `-u`）
4. 更新 `docs/PROGRESS.md`：在第一条 `---` 后插入记录
5. 把 progress 变更进入 Git 历史（策略 B：新 commit；策略 S：amend+force）
6. 防递归：用环境变量（例如 `OPENCODE_POST_COMMIT=1`）保护，避免自己触发自己

### 3.2 Root 级 pre-commit 框架（可选，但更像 spec）
你现在仓库是“后端用 pre-commit 框架、前端用 lint-staged、再加一些自定义 python 检查”。

如果要完全对齐 spec（`trailing-whitespace`/`check-merge-conflict`/`detect-private-key` 等），推荐新增 root `.pre-commit-config.yaml`，并在 `.husky/pre-commit` 中先跑 root pre-commit，再跑子项目检查。

> 但你现在 `.husky/pre-commit` 已经实现了 merge-conflict/private-key/大文件检查（用 python 内嵌脚本），所以 root pre-commit 不是硬性必须。

### 3.3 GitHub Actions：补齐 web/mobile 并修路径
- 修复：`.github/workflows/mobile.yml` 里 `working-directory` 和缓存路径改为 `solacore-mobile`
- 新增：`.github/workflows/web.yml`
  - `solacore-web`: `npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`
- （可选）新增统一：`.github/workflows/ci.yml` 作为总入口；等稳定后再收敛旧 workflow

## 4. 测试计划（执行器必须输出证据）

### 本地（必须）
1. **commit-msg gate**：`git commit -m "bad"` 必须失败
2. **pre-commit gate**：制造冲突标记 `<<<<<<<` 的 staged 文件，commit 必须失败
3. **post-commit**：一次正常 commit 后
   - 自动 push 发生
   - `docs/PROGRESS.md` 写入
   - 策略 B：出现新的 `docs(progress): ...` commit
4. **pre-push gate**：触发一次 push，确保会跑对应子项目检查（失败则拦截）

### 远程（必须）
- GitHub Actions 触发并通过（backend/web/mobile）

## 5. 你“要管的事”最终应该是什么

要做到你说的“我什么都不想管”，现实上你只需要提供：
- 你的需求/问题描述（自然语言）
- （一次性）确认是否允许我把代码推到 GitHub（写权限/账号已登录）

其余：实现、测试、提交、推送、记录进度，都由我执行。

## 6. 执行前最后一次确认（只需回答 1 句）

- 采用策略：`B`（安全推荐：新 commit 更新 PROGRESS）还是 `S`（严格贴 spec：amend+force）？
