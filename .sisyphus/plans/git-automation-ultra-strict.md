# Git 自动化（超严格、少操心）落地方案（Clarity / Solacore Monorepo）

> 目标：让你“尽量少管事”，并且 **严格按规范** 提交/推送；同时避免行业公认高风险的“hook 里自动 commit/amend/force-push”导致的历史污染与递归问题。

## 0. 你刚刚的选择

你回复 `a`，我按“最严格”解释为：

- **(A1) 后端 pre-commit：启用 `--all-files`**（最严格、可能慢）
- **(A2) pre-push：Web 强制 `npm run build`**（最严格）
- **(A3) pre-push：Mobile 强制 `tsc --noEmit`**（最严格）

如果你其实只想选其中一个 A（不是全选），告诉我你想严格在哪一块，我再收敛。

## 1. 先解释你问过的：`push` 是什么意思？

- `commit`：把改动保存到你本机的 Git 历史里（本地保存点）
- `push`：把本机的 commit **推送**到远程（比如 GitHub）

直觉类比：
- `commit` = 本地存档
- `push` = 上传到云端/共享给别人

## 2. 关键事实：你仓库现在 hook 的真实入口

- `.git/config` 里有 `core.hooksPath = .husky/_`
- 结论：**Git 实际执行的是 Husky 的 hooks**，不是 `.git/hooks/*`

当前已存在并会跑的 hook：
- `.husky/pre-commit`（已在 repo 里）

当前“应当存在但可能没被版本控制”的 hook（需要补齐）：
- `.husky/commit-msg`
- `.husky/pre-push`

## 3. 行业最佳实践（结合你给的 GIT-AUTOMATION-SPEC）与安全取舍

你给的 spec 想要：
- `git add . && git commit` 后一切自动跑
- 甚至 post-commit 自动 push、更新 `PROGRESS.md`

但根据调研与业界共识（以及你仓库是 monorepo + 多语言），**我建议严格自动化分层**：

### 3.1 本地：pre-commit（快、只做“立刻阻止低质量提交”的事）
- 格式化/静态检查/快速类型检查
- 失败 → 阻止 commit

### 3.2 本地：commit-msg（强制提交信息规范）
- 失败 → 阻止 commit（这一步越早越省事）

### 3.3 本地：pre-push（重、推送前最后闸门）
- 全量单测/覆盖率门槛/构建
- 失败 → 阻止 push

### 3.4 远端：GitHub Actions（最终裁决）
- PR & main 都跑

### 3.5 不建议：post-commit 自动 push / 自动 amend
原因（关键）：
- 容易把“你没 review 的格式化改动”偷偷写进历史
- 一旦失败会留下半脏状态，难救
- 自动 push 会制造大量碎提交触发 CI，历史噪音大

你想“少操心”，更安全的做法是：
- 让 `git push` 变成“按下按钮，先自动跑完所有校验，过了才真的推送”
- 这样你只需要记住：`git add -A && git commit -m "..." && git push`

## 4. 目标执行矩阵（落地后你会得到什么）

### 4.1 你日常只需要做

- `git add -A`
- `git commit -m "type(scope): subject"`
- `git push`

### 4.2 系统会自动做

- `git commit` 时：
  - 后端（若本次提交涉及 `solacore-api/`）：`poetry run pre-commit run --all-files`
  - web（若涉及 `solacore-web/`）：`npx lint-staged`
  - mobile（若涉及 `solacore-mobile/`）：`npx lint-staged`
  - 提交信息不合规 → 直接拒绝

- `git push` 时：
  - 后端（若变更涉及 api）：pytest + coverage gate 85%
  - web（若变更涉及 web）：`tsc --noEmit` + `npm run lint` + `npm run build`
  - mobile（若变更涉及 mobile）：`tsc --noEmit` + `npm run lint`

- 远端 CI（push/PR）：
  - 后端：ruff/mypy/pytest（当前 workflow 已存在）
  - web/mobile：需要补齐/修正现有 workflow 路径漂移（见第 7 节）

## 5. 需要改哪些文件（实现者照抄即可）

> 注意：本计划只定义改动点，不直接执行改动。要我实际落地实现，请你运行 `/start-work`。

### 5.1 修改：`.husky/pre-commit`

现状：web/mobile 用 `|| true` 吞掉失败，不严格。

目标：
- web/mobile：**去掉 `|| true`**
- api：按你选择 A1，改为 `pre-commit run --all-files`
- 仍保持“仅当 staged 里包含该子项目文件才触发”

### 5.2 新增：`.husky/commit-msg`

内容（复用后端已有脚本）：

```sh
#!/usr/bin/env sh
set -eu
ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$ROOT_DIR" || exit 1
python3 solacore-api/scripts/check-commit-msg.py "$1"
```

### 5.3 新增：`.husky/pre-push`

严格版（按 diff 范围判断是否涉及子项目，避免无关跑全套）：

- api：`poetry run pytest ... --cov-fail-under=85`
- web：`npx tsc --noEmit && npm run lint && npm run build`
- mobile：`npx tsc --noEmit && npm run lint`

### 5.4 对齐“唯一 hook 入口”

因为 `hooksPath` 已指向 Husky：
- `solacore-api/scripts/setup-hooks.sh`（pre-commit 框架安装 `.git/hooks`）会变得“看似成功但实际不跑”
- 方案：
  - 要么把它改成“只用于安装 python hooks 依赖，不写入 `.git/hooks`”，并在脚本里检测 hooksPath 给出提示
  - 要么在 `solacore-api/docs/CONTRIBUTING.md` 明确：本仓库 hook 以 Husky 为主

## 6. 你要的“我不想管”怎么做到极致（推荐）

在严格 hook 之上，再提供一个**一键命令**（不是 hook 自动 commit）：

- `scripts/publish "feat(api): ..."`
  - 自动：检查工作区 → `git add -A` → `git commit -m ...`（触发 hooks）→ `git push`（触发 pre-push）

这样你最后只需要记住一个命令。

（实现时会确保：失败就停下，不会静默继续。）

## 7. CI 需要修正/补齐的点（你仓库当前存在路径漂移）

现状扫描发现：
- 已有：`.github/workflows/backend.yml`（对 `solacore-api` 是有效的）
- 可能无效/漂移：`.github/workflows/api.yml`、`.github/workflows/deploy.yml`、`.github/workflows/mobile.yml` 使用 `clarity-*` 路径

严格方案建议：
- 修正 mobile workflow 工作目录为 `solacore-mobile`
- 新增或修正 web workflow：`solacore-web` 的 `lint` + `tsc --noEmit` + `build`

## 8. 验收清单（你不懂 git 也能判断“配置成功”）

1) 随便写一个不合规的 commit message：
- `git commit -m "hello"` 应该被拒绝，并提示格式

2) 在 `solacore-web` 随便制造一个 eslint 错误：
- `git commit` 应该被拒绝

3) 在 `solacore-api` 故意让测试失败：
- `git push` 应该被拒绝

## 9. 下一步

我现在只输出“严谨可落地的计划”。
- 如果你确认我对 `a` 的解释（A1+A2+A3 全部最严格），你回复：`确认严格`
- 然后你运行：`/start-work`

我会按本计划把所有文件改好，并确保：
- 你以后只需要 `git add -A && git commit -m "..." && git push`
- 任何不合规/测试不过都 **自动拦截**
