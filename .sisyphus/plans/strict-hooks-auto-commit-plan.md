# 严格提交与自动化 Hook 策略（OpenCode/Claude Code）

> 目标：你“什么都不懂也能安全提交”，并且做到**尽可能严格**、**可维护**、**不容易被绕过**。
>
> 关键原则（来自最佳实践 + 本仓库现状）：
> - **不要在 git hook 里自动 commit**（容易递归、产生“幽灵改动”、历史不可控）
> - **严格 = 失败就阻止 commit/push**，而不是帮你悄悄改完再提交
> - `pre-commit` 保持快（秒级）避免大家用 `--no-verify` 绕过
> - 把重活放在 `pre-push`（几十秒以内），更符合“分享前必须干净”

---

## 1. 你现在仓库的真实 Hook 链路（已核实）

- Git 配置：`.git/config` 有 `core.hooksPath = .husky/_`
  - 结论：**Git 实际调用的是 Husky 体系**，不是 `.git/hooks/*`
- 现有 Husky 脚本：`.husky/pre-commit`
  - 后端：`solacore-api` 运行 `poetry run pre-commit run --all-files`（会阻止 commit）
  - Web/Mobile：`lint-staged || true`（失败被忽略，属于漏洞）
- 后端 `pre-commit` 框架配置：`solacore-api/.pre-commit-config.yaml`
  - 定义了 `commit-msg` 校验（`scripts/check-commit-msg.py`）
  - 定义了 `pre-push` 测试覆盖率门槛（>=85%）
  - 但：这套 `commit-msg / pre-push` **只有在“安装成对应 hook 类型”时才会触发**；而现在 Git 的 hooksPath 指向 Husky，容易出现“配置写了但没跑”的错觉

---

## 2. 你说的“stop hook 令到你一直工作吗？”是什么

你看到的 `scope-check`/`stop` 是**OpenCode/Hookify 的对话规则**（提醒我汇报范围、统计改动），不是 git 的 `stop` hook。
- 它不会让 git 一直卡住
- 它最多让助手在“结束对话”时输出检查清单

---

## 3. 我替你做决定：三项开关的默认值（无需你理解）

为了做到“严格 + 不容易被绕过 + 不把人逼到 `--no-verify`”，我建议默认策略如下：

1) `pre-commit` 阶段后端是否 `--all-files`
- 选择：**B（否，只跑 staged/受影响文件）**
- 理由：`--all-files` 每次 commit 都全仓扫描，太慢会逼人绕过；把严格性放到 `pre-push` 更合理

2) `pre-push` 阶段 web 是否强制 `npm run build`
- 选择：**B（否，先跑 `tsc --noEmit` + lint/test）**
- 理由：`npm run build` 很慢且经常受环境影响；严格性建议由 CI 兜底（PR/Merge 必过 build）

3) Mobile 是否在 `pre-push` 强制 `tsc`
- 选择：**A（是，但只在 mobile 有改动时跑）**
- 理由：TS 类型错误是高频线上事故源；只在 mobile 相关改动时执行，严格且不拖慢其他提交

如果你坚持“极限严格”（不管慢不慢），可以把 1) 改成 A、2) 改成 A。

---

## 4. 目标态：严格但可用的 Hook 策略（推荐）

### 4.1 `commit-msg`（最严格、几乎不耗时）
目的：保证提交信息符合规范（Conventional Commits 类似格式）。
- 规则来源：已存在 `solacore-api/scripts/check-commit-msg.py`
- 触发方式：用 Husky 的 `.husky/commit-msg` 直接调用它（不依赖 pre-commit 安装）

### 4.2 `pre-commit`（快、只做“就地纠错”）
目的：提交前把格式/Lint 这类低成本问题挡住。
- Backend：`poetry run pre-commit run`（不加 `--all-files`）
- Web/Mobile：`npx lint-staged`
- 关键修复：**移除 `|| true`**，否则等于没设
- 只在对应子项目有 staged 变更时才运行（减少噪音/耗时）

### 4.3 `pre-push`（严格门槛：测试 + 类型检查）
目的：把“会破坏别人/CI 的东西”挡在 push 之前。
- Backend：`pytest --cov-fail-under=85`（仓库已经要求）
- Web：`npx tsc --noEmit`（可选再加 `npm test`，如果有）
- Mobile：`npx tsc --noEmit`（如果 mobile 有 tsconfig/可运行）
- 只在对应子项目有变更时运行

---

## 5. 需要新增/修改的 Hook 文件（建议内容，供实现者照抄）

> 注意：本节是“实施说明”，用于你之后运行 `/start-work` 让实现代理真正落地修改。

### 5.1 修改 `.husky/pre-commit`
- 修复点：移除 `|| true`
- 优化点：只在 staged 变更涉及该目录时执行
- 后端不再 `--all-files`

伪代码结构：
- 定义 `changed_in <dir>`：用 `git diff --cached --name-only --diff-filter=ACMR` 判断
- `if changed_in solacore-api; then cd solacore-api; poetry run pre-commit run; fi`
- `if changed_in solacore-web; then cd solacore-web; npx lint-staged; fi`
- `if changed_in solacore-mobile; then cd solacore-mobile; npx lint-staged; fi`

### 5.2 新增 `.husky/commit-msg`
- 调用 `solacore-api/scripts/check-commit-msg.py` 校验 `$1`（commit message file）

伪代码：
- `python solacore-api/scripts/check-commit-msg.py "$1"`

### 5.3 新增 `.husky/pre-push`
- Backend：进入 `solacore-api`，执行覆盖率测试门槛
- Web：仅当 web 有改动时，执行 `npx tsc --noEmit`
- Mobile：仅当 mobile 有改动时，执行 `npx tsc --noEmit`

### 5.4 对齐“安装入口”（避免 split-brain）
当前 `solacore-api/scripts/setup-hooks.sh` 安装的是 pre-commit hooks，但由于 `core.hooksPath` 指向 Husky，这个脚本会让人误以为装好了。
两种选择（二选一）：
- 方案 A（推荐）：把 `setup-hooks.sh` 改为提示“此仓库使用 Husky”，并检查 `.husky/*` 是否存在
- 方案 B：移除 `core.hooksPath`，全部回归 pre-commit 框架（不推荐：web/mobile 已在用 husky/lint-staged）

---

## 6. 你想要“我自动帮你提交”的现实做法（严格且安全）

你要的是：你不用理解命令，但提交必须符合规范。
最佳实践不是“hook 自动 commit”，而是“**我（助手）执行一个严格的提交流程**”。

推荐的自动化流程（由助手执行）：
1. 检查工作区状态（避免误提交）
2. 只 add 相关文件（避免把不该提交的带进去）
3. 运行严格校验（等同于 pre-commit + pre-push）
4. 生成符合格式的 commit message
5. 执行 `git commit`
6. （可选）再执行 `git push`（只有你明确要求我 push 才做）

这就是你说的“依赖我完成”，同时保证最严格。

---

## 7. 下一步怎么做（你不用懂命令）

我现在是“规划模式”，不会直接改代码。
- 你要我自动把 hook 配好并自动提交：请你运行 `/start-work`
- `/start-work` 之后，实现代理会按本计划：
  - 修复 `.husky/pre-commit` 的漏洞（去掉 `|| true`）
  - 加上 `.husky/commit-msg` 和 `.husky/pre-push`
  - 让提交/推送前的检查真正严格生效
