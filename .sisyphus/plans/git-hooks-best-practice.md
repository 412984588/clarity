# Git Hooks 最佳实践策略（本仓库：clarity/solacore）

> 目标：让“提交前有检查、提交信息规范、推送前跑测试”变成默认行为，同时避免自动提交带来的递归/混乱历史

## 1. 先回答你问的两个点

### 1) 我工作时输出能不能中文
可以。后续我每一步都会用中文说明「我现在在做什么 / 为什么做 / 下一步是什么」，并尽量用短句让你能跟上。

### 2) “stop hook”会不会导致我一直工作
不会。
- Husky / pre-commit 的 `stop` 通常只是触发一个“结束提示/统计”（例如 scope-check）
- 它不会自动再次触发 git hook，也不会形成循环
- 你看到我“持续在干活”是因为你在一个请求里让我要“修复 + 跑测试 + 回归”，我就把整套流程做完了

## 2. 现状扫描（你仓库当前 hook 结构）

### Git 实际 hook 入口
- `.git/config` 配置了 `core.hooksPath = .husky/_`
- 代表：Git 执行 hook 时，入口来自 Husky 目录，而不是默认的 `.git/hooks/*`

### 当前会发生什么
- `git commit`：会跑根目录 `.husky/pre-commit`
  - `solacore-api`：`poetry run pre-commit run --all-files`（很重，但会阻止提交）
  - `solacore-web`：`npx lint-staged || true`（失败会被忽略）
  - `solacore-mobile`：`npx lint-staged || true`（失败会被忽略）
- `commit-msg`：目前 Husky 侧没看到强制；但 `solacore-api/.pre-commit-config.yaml` 里定义了 `commit-msg-format`（需要安装 pre-commit 的 commit-msg hook 才会生效）
- `pre-push`：Husky 侧没看到；`solacore-api/.pre-commit-config.yaml` 有 `pytest-coverage`（同样需要安装 pre-commit 的 pre-push hook 才会生效）

### 当前风险点（必须修）
- web/mobile 的 `lint-staged` 失败被 `|| true` 吞掉 → 代码质量约束形同虚设
- 后端 `pre-commit run --all-files` 每次 commit 都全量跑 → 容易变慢，导致人为绕过（`--no-verify`）
- hook “双体系”风险：repo 用 Husky hooksPath，但 backend 又提供 `pre-commit install` 到 `.git/hooks` 的脚本 → 实际可能不生效，容易误判

## 3. 你想要的“自动提交”——最佳实践怎么做

### 结论（行业最佳实践）
不建议用 git hooks 做“自动 commit”（在 hook 里 `git commit` / `git commit --amend`），原因：
- 容易递归（post-commit 触发 commit 再触发 post-commit…）
- 容易产生你没 review 的“幽灵改动”（格式化/修复被悄悄提交）
- 一旦半路失败会留下脏状态（部分文件被改/未 stage）

### 更安全的“自动化体验”替代方案（推荐）
1) **Hook 负责“拦截不合格提交/推送”**（Gatekeeping）
2) **提供一个“一键提交命令”**（Wrapper），让你不懂 git 细节也能用

你最终体验会是：
- 平时你只需要运行一个命令（例如 `./scripts/commit "fix(api): ..."`）
- 它会按顺序：格式化/静态检查 → 跑测试 → 通过后再真正执行 `git commit`
- Hook 仍然存在，防止你绕过

## 4. 推荐策略（MECE）

### A. commit-msg（强约束）
- 强制 Conventional Commits：`type(scope): subject`
- 先用现有的 `solacore-api/scripts/check-commit-msg.py`（已经写好）
- 在 Husky 新增 `.husky/commit-msg`，调用这个脚本（最小改动，立即生效）

### B. pre-commit（快、只做轻量）
目标：< 2-3 秒
- API：不再 `--all-files`；改为只对 staged 变更执行（或仅对 `solacore-api/` 变更执行）
- Web/Mobile：保留 `lint-staged`，但去掉 `|| true`，失败就阻止提交
- 优化：只有当 staged 里存在对应目录文件时，才进入该子项目执行检查（避免无关项目被触发）

### C. pre-push（重、作为质量闸门）
目标：< 30-60 秒
- API：跑 `pytest`（可用你们现有 coverage gate 85% 作为强约束）
- Web：跑 `npx tsc --noEmit`（类型检查）+（如有）单元测试
- Mobile：跑 `npx tsc --noEmit` + lint（可选）

### D. CI（最终裁决）
- PR：跑增量检查（`pre-commit run --from-ref ... --to-ref ...`）
- main：跑全量检查（`pre-commit run --all-files` + full tests）

## 5. 具体落地步骤（给 /start-work 用）

> 我是 planner，这里给可执行步骤；你要我改代码就运行 `/start-work`

1) 新增 Husky hook：`.husky/commit-msg`
   - 调用：`python solacore-api/scripts/check-commit-msg.py "$1"`
2) 修改 `.husky/pre-commit`
   - 去掉 web/mobile 的 `|| true`
   - 把后端 `pre-commit run --all-files` 改为 staged-only（或仅 api 变更时才跑）
3) 新增 `.husky/pre-push`
   - API：`cd solacore-api && poetry run pytest ...`
   - Web：`cd solacore-web && npx tsc --noEmit`（可选加 test）
   - Mobile：`cd solacore-mobile && npx tsc --noEmit`（可选）
4) 对齐 “安装入口”
   - 明确：以 Husky hooksPath 为主，不再依赖 `.git/hooks`
   - 更新 `solacore-api/scripts/setup-hooks.sh`（或文档）避免误导
5) 增加一键命令（可选但强烈推荐）
   - `scripts/commit`：把“跑检查+测试+commit”串起来，让你只记一个命令

## 6. 需要你确认的 3 个选择（不确认我无法做最终落地）

1) 你希望 pre-commit 阶段跑到什么程度
- 选项：A 只跑 lint/format（推荐） / B 也跑快速单测

2) 你希望 pre-push 阶段是否强制跑全量后端 pytest + coverage
- 选项：A 强制（最安全） / B 只跑关键子集（更快）

3) Conventional Commit 的 scope 规则
- 选项：A 允许任意 scope（宽松） / B 仅允许 `api|web|mobile|docs|ci|repo`（更规范）

---

如果你确认以上 3 点，我就能把具体改动清单定死，然后你运行 `/start-work` 我再按策略落地实现
