# OpenCode Git 自动化（严格版）落地计划（对齐 GIT-AUTOMATION-SPEC v1.0）

> 目的：让你“少管事”，把质量门槛/推送/进度记录自动化起来
> 
> 约束：本仓库当前实际 hook 入口是 Husky（`.git/config` 的 `core.hooksPath=.husky/_`），所以必须把自动化落在 `.husky/`，不能再依赖 `.git/hooks/*`

---

## 0. 成功标准（验收口径）

### 功能性（Functional）
1. 执行 `git commit -m "<conventional message>"` 时，自动跑“Pre-commit 检查”（失败则阻止提交）
2. commit 成功后，自动执行：
   - 自动 push 到 `origin/<当前分支>`（失败要给出明确提示，不要静默）
   - 自动更新 `docs/PROGRESS.md`（在顶部插入一条记录）
   - 更新后自动 `--amend` 并再次 push（按规范要求）
3. 执行 `git push` 时，自动跑“Pre-push 测试”（失败则阻止 push）
4. push 到远程后，GitHub Actions 自动跑 CI（至少覆盖：backend + web + mobile + pre-commit 全量）

### 可观察（Observable）
- 本地终端能看到每个 hook 的开始/成功/失败输出
- `docs/PROGRESS.md` 会新增一条带时间戳的记录
- GitHub Actions 在 PR 与 push 时能看到对应 workflow 运行

### 通过/失败（Pass/Fail）
- 任一检查失败：commit/push 必须被拒绝（exit code != 0）
- 任何“自动化脚本修改了文件”：必须要求重新 `git add` 再 commit（或由 post-commit 的 amend 机制处理）

---

## 1. 当前现状（来自扫描证据）

### 已存在（可复用）
- Husky hook 入口生效：`.git/config` 有 `hooksPath = .husky/_`
- 现有 `pre-commit`：`.husky/pre-commit` 已按子项目判断执行
  - `solacore-api`：`poetry run pre-commit run`
  - `solacore-web`：`npx lint-staged`
  - `solacore-mobile`：`npx lint-staged`
- `commit-msg` 校验脚本已存在：`solacore-api/scripts/check-commit-msg.py`
- `solacore-api/.pre-commit-config.yaml` 已配置 ruff/isort/mypy + pre-push pytest coverage gate
- 后端 CI 已存在：`.github/workflows/backend.yml`（但数据库名/路径仍有历史遗留命名）

### 缺口（必须补齐）
- 没有 post-commit 自动化（“自动 push + PROGRESS 更新 + amend + force-with-lease” 尚未真正纳入 Husky 流程）
- mobile CI workflow 路径明显不对：`.github/workflows/mobile.yml` 指向 `clarity-mobile`，仓库实际是 `solacore-mobile`
- 缺少 web CI workflow（对 `solacore-web` 的 lint/typecheck/build）
- 规范文档的 `.git/hooks/post-commit` 与本仓库 Husky `hooksPath` 冲突（需要改成 Husky 版本）

---

## 2. 设计决策（严格 + 少操心）

### 2.1 “单一入口原则”
- 以 Husky 作为唯一 hook 入口（因为 Git 已配置 `hooksPath`）
- 禁止再依赖 `.git/hooks/*` 的手工脚本，否则会出现“你以为生效，其实没运行”的错觉

### 2.2 “严格程度选择”（你已选 A：最严格）
- Pre-commit：必须严格失败即拦截；允许自动修复（格式化）但要可见、可重复
- Pre-push：跑更重的测试/构建（失败即阻止 push）
- Post-commit：按你的规范实现“自动 push + PROGRESS 更新 + amend + force-with-lease”

> 备注：行业最佳实践一般不推荐 auto-push/auto-amend，但你明确要求“完全自动化 + 我不想管”，这里按你的规范执行，同时加防递归保护（否则会死循环）

---

## 3. 需要实现/修改的文件（执行器照抄清单）

> 下面每个文件都要纳入 git 跟踪（不能是 untracked）

### 3.1 Husky hooks（本地）

1) 新增：`.husky/post-commit`
- 作用：commit 成功后自动 push + 更新 `docs/PROGRESS.md` + amend + force-with-lease
- 必须做的安全护栏：防止递归
  - 方案：在 hook 顶部判断环境变量 `OPENCODE_POST_COMMIT=1` 则直接退出
  - 在 hook 内部执行 amend 前 `export OPENCODE_POST_COMMIT=1`

2) 新增：`.husky/_/post-commit`
- 内容应与现有 `.husky/_/pre-commit` 一样，只有两行：
  - `#!/usr/bin/env sh`
  - `. "$(dirname "$0")/h"`

3) 确认存在并纳入版本管理：`.husky/commit-msg`（你现在已经有，但要确保被 git track）
- 内容：调用 `python3 solacore-api/scripts/check-commit-msg.py "$1"`

4) 确认存在并纳入版本管理：`.husky/pre-push`（你现在已经有，但要确保被 git track）
- 严格版建议调整为：
  - 后端：pytest + coverage gate（沿用 85%）
  - web：`npm run build`（严格） + `npx tsc --noEmit`（可选重复但无害）
  - mobile：`npx tsc --noEmit`（严格） + `npm run lint`

5) 修改：`.husky/pre-commit`
- 目标：把“规范文档要求的通用检查 + prettier/markdownlint”补齐
- 两种实现路径（二选一，推荐 A）

A. 通过 root `pre-commit` 配置统一跑（更接近规范文档）
- 新增根目录 `.pre-commit-config.yaml`（见 3.2）
- 在 `.husky/pre-commit` 中加入：
  - `cd solacore-api && poetry run pre-commit run --config "$ROOT_DIR/.pre-commit-config.yaml" --hook-stage pre-commit`
  - 然后再执行现有按子项目的检查（或把子项目检查也整合到 root config 的 local hooks）

B. 纯 shell + npm 实现通用检查（不引入 root pre-commit）
- 用 `git diff --cached --check` 做 whitespace 检查
- 用 `git diff --cached --name-only` + grep 检查 merge-conflict markers
- 用 `git diff --cached --name-only` + size 检查大文件
- 用 `gitleaks`/自写脚本做密钥检测（实现成本高，不推荐）

> 推荐 A：因为你规范里明确写了 pre-commit-hooks/mirrors-prettier/markdownlint-cli，这套天然适配

### 3.2 根目录 Pre-commit 配置（与规范文档一致）

新增：`.pre-commit-config.yaml`（仓库根目录）
- 内容按 `GIT-AUTOMATION-SPEC.md` 的 hooks：
  - pre-commit-hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-merge-conflict, check-added-large-files, detect-private-key
  - local: show-git-diff
  - prettier mirror
  - markdownlint-cli --fix
  - local(pre-push): run-tests（在本仓库要改成根据子项目跑：api/web/mobile，而不是 `npm test` 一刀切）

关键点：
- 要配置 `exclude`：node_modules/.git/.tmp-/__pycache__ 等
- prettier types：js/jsx/ts/tsx/json/md/yaml

### 3.3 GitHub Actions（远程）

目标：补齐 web/mobile CI，并让 CI 作为最终兜底

1) 修复：`.github/workflows/mobile.yml`
- `working-directory` 改为 `solacore-mobile`
- `cache-dependency-path` 改为 `solacore-mobile/package-lock.json`

2) 新增：`.github/workflows/web.yml`（或合并进统一 `ci.yml`）
- 工作目录：`solacore-web`
- 运行：`npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`

3) 新增：`.github/workflows/ci.yml`（统一入口，符合规范文档）
- 触发：push/pull_request（main/master/develop）
- job1: `pre-commit run --all-files`（需要 python + pre-commit）
- job2: backend（ruff/mypy/pytest）
- job3: web（lint/tsc/build）
- job4: mobile（lint/tsc）

> 注意：本仓库已有 `backend.yml`，可以选择保留并新增统一 `ci.yml`，或者把 backend.yml 融进 ci.yml 后删掉旧的。推荐：先新增 ci.yml，验证稳定后再收敛

---

## 4. Post-commit 脚本细节（必须严格照规范，但避免死循环）

你规范文档的 post-commit 做了 3 件事：push → 更新 PROGRESS → amend → force-with-lease

执行器实现要点：
1) 先 push（普通 push；若失败尝试 `-u`）
2) 如果 `docs/PROGRESS.md` 存在：插入记录（以 `---` 分隔线作为插入点）
3) `git add docs/PROGRESS.md`
4) `OPENCODE_POST_COMMIT=1 git commit --amend --no-edit`（关键：避免再次触发 post-commit）
5) `git push --force-with-lease`（按规范要求）

输出要求：
- 每一步要 echo 清晰状态（你希望“我在干什么”）
- 失败要 exit 非 0（或至少明确提示并 exit 0 的理由）

---

## 5. 测试计划（执行器必须给出证据）

### Objective
验证：commit/push/CI 链路按规范自洽

### Test Cases
1) Commit-msg gate
- 输入：`git commit -m "bad message"`
- 预期：commit 被拒绝

2) Pre-commit gate
- 输入：制造一个包含 merge conflict marker 的 staged 文件
- 预期：commit 被拒绝

3) Auto-fix gate
- 输入：制造一个带行尾空格、缺少文件末尾换行的 staged 文件
- 预期：pre-commit 自动修复并拒绝本次 commit，提示重新 add

4) Post-commit automation
- 输入：提交一个合法 commit
- 预期：自动 push；`docs/PROGRESS.md` 顶部新增记录；随后发生 amend；随后 force-with-lease push

5) Pre-push tests
- 输入：触发 `git push`
- 预期：在 push 前自动跑测试/构建；失败则阻止 push

6) CI
- 输入：推送到远程（PR 或 push）
- 预期：GitHub Actions 中 `ci.yml` 相关 jobs 全部出现并运行

### How to Execute
执行器在一个临时分支上验证，避免污染 `main`

---

## 6. 交付物清单（最终应出现在仓库里）

- `.husky/post-commit`
- `.husky/_/post-commit`
- `.husky/commit-msg`（已存在但需纳入 git）
- `.husky/pre-push`（已存在但需纳入 git，且按严格版调整）
- `.husky/pre-commit`（补齐通用检查/对齐 root pre-commit）
- `.pre-commit-config.yaml`（根目录）
- `.github/workflows/ci.yml`
- `.github/workflows/web.yml`（或合并到 ci.yml）
- 修复后的 `.github/workflows/mobile.yml`

---

## 7. 对你“我不想管”的最终体验承诺

完成一次性配置后，你日常只需要：
- 你说需求（例如“修复登录 bug”）
- 我/执行器实现 + 自测 + 按规范自动提交 + 自动推送 + 自动记录进度

你不需要记一堆 git 命令，也不需要懂编程
