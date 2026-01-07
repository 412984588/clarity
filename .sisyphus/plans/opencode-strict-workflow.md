# OpenCode 严格工作流（Hooks + 提交策略）

> 目标：在 **OpenCode/Claude Code** 的协作模式下做到“严格且可用”：
> - 本地提交前自动执行校验（lint/format/typecheck/tests）
> - 提交信息强制符合规范
> - 不允许“悄悄改代码就提交”（避免历史污染、递归、不可预期差异）
> - **默认不自动 push**（push 属于发布动作，需显式触发）

---

## 0. 你现在仓库的真实现状（已确认）

- Git 使用 Husky：`.git/config` 里 `core.hooksPath = .husky/_`
- 当前只有 `.husky/pre-commit`，没有看到 `.husky/commit-msg` / `.husky/pre-push`
- `.husky/pre-commit` 的问题：
  - 后端：`poetry run pre-commit run --all-files`（严格但可能很慢）
  - Web/Mobile：`npx lint-staged || true`（**失败被忽略**，不严格）
- 后端 `solacore-api/.pre-commit-config.yaml` 已定义：
  - `commit-msg`：`scripts/check-commit-msg.py`
  - `pre-push`：`pytest --cov-fail-under=85`
  - 但由于 hook 入口在 Husky，`pre-commit install --hook-type ...` 这套可能并未生效（“分裂大脑”风险）

---

## 1. 最严格但可用：推荐策略（B 策略）

**策略 B：以 Husky 为唯一入口**，把所有阶段的“强制校验”都集中在：
- `.husky/pre-commit`：只做“快检查（秒级）”，并且 **失败就阻止 commit**
- `.husky/commit-msg`：强制 commit message 规范
- `.husky/pre-push`：做“重检查（几十秒~几分钟）”，并且 **失败就阻止 push**

理由：
- 单入口避免 `.git/hooks/*` 与 `hooksPath` 的冲突
- 严格校验必须“不可被忽略”，所以不能再用 `|| true`
- 重检查放在 `pre-push`，否则 dev 会频繁 `--no-verify` 绕过

---

## 2. 具体要改/新增的 hook 文件（实施清单）

### 2.1 `.husky/pre-commit`（严格版）
目标：< 10 秒，失败就 block commit

建议内容：
1) Backend（solacore-api）
- `poetry run pre-commit run`（不要 `--all-files`，默认对 staged/变更文件更快）
- 可选：`poetry run mypy app`（如果你真的要最严格，可以放这里，但会慢）

2) Web（solacore-web）
- **只在有 web 变更时**运行：`npx lint-staged`（失败就退出）
- 不要 `|| true`

3) Mobile（solacore-mobile）
- 同理：有 mobile 变更才运行 `npx lint-staged`

> 关键点：如果某子项目没有改动，就别跑它的校验（避免过慢导致绕过）

### 2.2 `.husky/commit-msg`
目标：强制 `<type>(<scope>): <subject>`

建议：复用后端现有脚本：
- `python solacore-api/scripts/check-commit-msg.py "$1"`

好处：不用引入 commitlint 依赖，也符合你现在的 CONTRIBUTING.md

### 2.3 `.husky/pre-push`
目标：最严格的“推送门禁”，失败阻止 push

建议内容：
- Backend：`cd solacore-api && poetry run pytest -q --maxfail=1 --disable-warnings --cov=app --cov-fail-under=85`
- Web：`cd solacore-web && npx tsc --noEmit && npm run lint`（可选：如果你有单测，再加 `npm test`）
- Mobile：`cd solacore-mobile && npx tsc --noEmit && npm run lint`

> 注意：如果你希望 push 时也只检查“受影响项目”，也可以做变更路径判断

---

## 3. OpenCode（你说的“给 opencode 的设定”）严格规则建议

你想要的是：**我（AI）以后“自动帮你提交”，但必须严格**。
这件事分两层：

### 3.1 仓库层（任何人/任何工具都严格）
用上面的 Husky 三件套把质量门禁钉死（最关键）

### 3.2 OpenCode/Claude Code 层（AI 行为约束）
建议增加“强制流程”规则：
- 只有当 `git diff` 为空且 `git status` 显示 staged changes 才允许 `git commit`
- `git commit` 前必须跑：
  - 对应子项目 lint/format
  - 对应子项目 tests
- commit message 必须通过校验脚本
- 默认 **不 push**，除非用户明确说“推送”

实现方式（任选其一）：
- A) 用 Hookify/Claude Code 的 rules（prompt/tool 级别拦截）
- B) 用一个 `scripts/strict-commit.sh` wrapper，OpenCode 永远调用这个脚本（最稳）

---

## 4. “自动帮我提交”到底怎么定义（必须先对齐）

为了做到“严格”，需要你确认 3 个点（这决定最终方案）：

1) 你说的“自动提交”是：
- A. 我在你说“提交”时，自动完成 `git add` + `git commit`（推荐）
- B. 我不等你说“提交”，只要有改动就自动提交（强烈不推荐，会污染历史）

2) 是否允许自动选择 commit message？
- A. 我根据 diff 自动生成 message（推荐，但每次给你确认一次）
- B. 你手动输入 message（最严格）

3) 是否允许自动 push？
- A. 永不自动 push（推荐）
- B. 通过 hooks 后自动 push（风险高，等同发布）

---

## 5. 交付物

- 我会输出一个“最终版本”的严格策略（含具体 hook 内容与变更文件清单）
- 你运行 `/start-work` 后，我再按该计划去实施修改、跑测试、按规范提交（必要时分多次 commit）

