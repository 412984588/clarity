# 严格提交（Strict Commit）最佳实践方案（本仓库适配）

> 目标：让“提交前必跑检查、消息必合规、推送前必跑测试”变成默认行为；同时避免 **hook 里自动提交** 这种高风险模式

## 0. 结论先说（策略 B：严格但可用）

- **不建议/不实现 hook 自动提交**：会带来递归、历史污染、悄悄改代码、难排查等风险（业界共识）
- **严格标准的实现方式**：
  - `commit-msg`：强制 Conventional Commit 格式（阻止不合规 commit）
  - `pre-commit`：只跑 **快检查**（格式化/静态检查/类型检查），目标 < 3 秒；失败直接阻止 commit
  - `pre-push`：跑 **完整单测 + 覆盖率门槛**（以及 TS typecheck），失败阻止 push
  - CI：再跑全量（可 `--all-files`），作为最终兜底

## 1. 你现在仓库的真实现状（关键点）

- 你的 Git 配置：`.git/config` 里 `core.hooksPath = .husky/_`
  - 结论：Git 实际调用的是 Husky 管理的 hooks（`.husky/_/*` 作为入口，由 `.husky/_/h` 路由到 `.husky/<hook>`）
- 目前只有 `.husky/pre-commit` 存在且会执行
  - Backend：`poetry run pre-commit run --all-files`（严格但重）
  - Web/Mobile：`npx lint-staged || true`（**失败被忽略**，不严格）
- `solacore-api/.pre-commit-config.yaml` 里确实定义了：
  - `commit-msg`：`scripts/check-commit-msg.py`
  - `pre-push`：`pytest --cov-fail-under=85`
  - 但这些 **只有在 pre-commit 安装了对应 hook-type 并且 Git 走 .git/hooks/** 时才可靠
  - 现在 `hooksPath` 指向 Husky，`.git/hooks/*` 可能不会生效 → 有“分裂大脑”的风险

## 2. 严格策略（推荐）

### 2.1 统一入口：全部以 Husky 作为唯一 hook 入口

原因：你已经在用 Husky 的 `hooksPath`，最稳妥是把“严格规范”全部放在 `.husky/` 下，避免 `.git/hooks` 与 Husky 并存导致实际未生效

### 2.2 具体 hook 设计

#### A) `.husky/commit-msg`（强制 commit message 格式）

- 直接复用后端已有脚本：`solacore-api/scripts/check-commit-msg.py`
- 这样不依赖 node 生态 commitlint，也不额外引入依赖

建议内容：
```sh
#!/usr/bin/env sh
set -eu
python3 solacore-api/scripts/check-commit-msg.py "$1"
```

#### B) `.husky/pre-commit`（快检查：严格失败，不忽略）

目标：只跑“会阻止你提交脏代码”的快检查；不要跑全量单测

建议流程（严格版）：
1) Backend：`cd solacore-api && poetry run pre-commit run`（不要 `--all-files`，默认对 staged 文件）
2) Web：`cd solacore-web && npx lint-staged`（去掉 `|| true`）
3) Mobile：`cd solacore-mobile && npx lint-staged`（去掉 `|| true`）

建议内容：
```sh
#!/usr/bin/env sh
set -eu
ROOT_DIR=$(git rev-parse --show-toplevel)

cd "$ROOT_DIR/solacore-api"
poetry run pre-commit run

cd "$ROOT_DIR/solacore-web"
npx lint-staged

cd "$ROOT_DIR/solacore-mobile"
npx lint-staged
```

> 如果担心性能：可以在 pre-commit 里按 git diff 判断目录是否有 staged 变更再跑对应检查

#### C) `.husky/pre-push`（慢检查：单测 + 覆盖率门槛 + TS typecheck）

建议流程（严格版）：
1) Backend：`poetry run pytest --cov=app --cov-fail-under=85 --maxfail=1`
2) Web：`npx tsc --noEmit`（可选再跑 `npm test`）
3) Mobile：`npx tsc --noEmit`（如果移动端有配置；否则只跑 lint-staged 已覆盖格式）

建议内容：
```sh
#!/usr/bin/env sh
set -eu
ROOT_DIR=$(git rev-parse --show-toplevel)

cd "$ROOT_DIR/solacore-api"
poetry run pytest -q --maxfail=1 --disable-warnings --cov=app --cov-fail-under=85

cd "$ROOT_DIR/solacore-web"
npx tsc --noEmit

cd "$ROOT_DIR/solacore-mobile"
npx tsc --noEmit || true
```

> 说明：mobile 的 `tsc` 可能未配置/较慢，可先 `|| true` 或移除，由你决定“严格程度”

## 3. 为什么不做“hook 自动提交”

- `post-commit` / `pre-commit` 里再触发 `git commit` 很容易递归
- 自动修改并提交会造成“我没看过却进了历史”的幽灵变更
- 一旦 hook 半路失败会留下脏 index/working tree，反而更难救

替代方案（同样达到“强制规范”）：
- hook 负责 **阻止不合规**（fail fast）
- 提交动作还是由人触发（可配合 `npm run commit` / wrapper 脚本）

## 4. 提交执行手册（给不熟 git 的你）

### 日常最简单流程
1) 写代码
2) `git add -A`
3) `git commit -m "fix(api): align mobile auth tokens"`
4) `git push`

如果 hook 失败：
- 失败信息会告诉你是哪个环节（格式/检查/测试）
- 按提示修复后再次 `git add -A` 和 `git commit ...`

### 推荐 commit message 模板
- `fix(api): ...`
- `feat(web): ...`
- `chore(repo): ...`

> 你现在后端脚本只校验 `type(scope): subject`，scope 可先用 `api/web/mobile/repo/docs/ci`

## 5. 变更点清单（给实现者照抄）

- 新增：`.husky/commit-msg`
- 新增：`.husky/pre-push`
- 修改：`.husky/pre-commit`：
  - 移除 `--all-files`
  - 移除 web/mobile 的 `|| true`

（可选优化）
- 修改 `solacore-api/.pre-commit-config.yaml`：
  - 增加 `files:` 过滤，避免在非后端改动时启动 python hook

## 6. 风险/回滚

- 若 pre-commit 太慢：先把重测试留到 pre-push/CI；pre-commit 只做 ruff/format/mypy
- 回滚：删除新增的 `.husky/commit-msg`、`.husky/pre-push`，恢复旧版 `.husky/pre-commit`
