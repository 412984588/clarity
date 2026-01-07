# Strict Hooks + CI Workflow (OpenCode)

> 目标：尽量“你不用管”，同时做到“最严格的规范”。
>
> 解释：Git 的“严格”= 任何不合规的代码/提交信息/测试失败都不能进入远程仓库。
> 最佳实践通常是：
> - **pre-commit** 做“快且必过”的检查（格式化/静态检查/小范围），避免太慢导致大家绕过
> - **pre-push** 做“更重”的检查（测试/覆盖率/类型检查）
> - **CI** 做“最终裁判”（全量测试、覆盖率、安全扫描），强制 PR/merge 规则
>
---

## 0. 你问的“push”是什么意思？

- `commit`：把改动**记录到你本机的 Git 历史**（只在本地）
- `push`：把你本机的提交**上传到 GitHub 远程仓库**（别人/CI 才能看到）
- 所以“**不 push**”= 只在本地形成提交记录，但**不上传**。

为什么很多团队会说“我可以帮你自动 commit，但先不 push”？
- 因为 push 会影响共享仓库（main 分支尤其敏感），通常需要：分支策略、PR、CI 都到位以后再自动化。

---

## 1. 当前仓库 hook 现状（已确认）

### 1.1 Git 实际调用的 hooks
- 仓库配置了 `core.hooksPath = .husky/_`（见 `.git/config`）
- Husky 的 runner：`.husky/_/h`，它会去执行同名脚本：`.husky/pre-commit`、`.husky/commit-msg`、`.husky/pre-push` 等

### 1.2 已存在/已发现的问题点
- 之前 `.husky/pre-commit` 对 web/mobile 失败是 `|| true`（会忽略失败）——这不严格
- `solacore-api/.pre-commit-config.yaml` 里定义了 `commit-msg` / `pre-push`，但如果没有正确安装到 hooksPath，会出现“看起来有规则、实际没生效”的分裂

---

## 2. 推荐目标状态（最少你操心 + 严格）

### 2.1 你需要做的日常动作（最少）
- 只需要：
  1) `git add ...`
  2) `git commit -m "type(scope): subject"`
  3) `git push`

其它都交给 hooks + CI。

### 2.2 严格规则落点
- `commit-msg`：强制提交信息格式（Conventional Commits）
- `pre-commit`：快速校验（lint/format/静态检查）+ 自动修复（允许修复，但**失败则阻止提交**）
- `pre-push`：重校验（pytest 覆盖率门槛、tsc、web build 可选）
- CI：全量校验 + PR 保护（不通过无法合并到 main）

---

## 3. Husky 方案（严谨 wiring，单一入口）

### 3.1 必备文件（建议存在于 repo root）
- `.husky/pre-commit`：
  - 只对本次 staged 涉及的子项目运行检查
  - 任意一个子项目检查失败 => 直接阻止提交
- `.husky/commit-msg`：
  - 复用 `solacore-api/scripts/check-commit-msg.py` 校验提交信息
- `.husky/pre-push`：
  - 针对本次 push 涉及的子项目跑“重检查”

### 3.2 强烈建议：不要做“自动提交/自动 push”
- 不建议在 hook 里 `git commit` 或 `git push`
- 原因：递归触发、历史污染、难追踪、容易产生“我没看过但被提交了”的风险

如果你坚持“越自动越好”，最安全替代是：
- 提供一个统一命令（wrapper）：`./scripts/commit` 或 `npm run commit`
- 它在**commit 之前**跑完所有检查/测试，成功后再执行 `git commit`

---

## 4. pre-commit / pre-push 的严格策略（默认选择）

你之前那 3 个“开关”，我这里直接替你选“最少操心但仍然严格”的默认：

1) 后端 `pre-commit` 是否 `--all-files`：**选 B（staged only）**
- 理由：`--all-files` 过慢会逼人绕过 hooks，严格反而失效

2) `pre-push` web 是否强制 `npm run build`：**选 B（不强制 build）**
- 理由：build 很慢，放到 CI 更合适；本地 pre-push 先用 `tsc + lint` 把大坑挡住

3) Mobile `pre-push` 是否强制 `tsc`：**选 A（强制 tsc）**
- 理由：mobile 项目类型错误很常见，`tsc --noEmit` 相对可控，收益高

如果你更偏“极致严格”，把 (2) 改为 A：push 前也强制 build，但体验会明显变慢。

---

## 5. CI 方案（GitHub Actions）

目标：只要 push/PR，就自动跑：
- API：ruff + mypy + pytest(含 coverage gate)
- Web：npm ci + lint + tsc + build
- Mobile：npm ci + lint + tsc（以及可选的 EAS dry-run）

关键点：
- **路径过滤**：只在相关目录变更时跑对应 job（减少 CI 时间）
- **PR 保护**：要求 checks 全绿才能 merge

---

## 6. 实施步骤（给“实现者”执行）

> 我是 planner：我产出方案和文件清单；你后续用 `/start-work` 让我进入实现模式，或你自己照步骤改。

1) 在 repo root 创建/更新：
- `.husky/pre-commit`
- `.husky/commit-msg`
- `.husky/pre-push`

2) 去掉任何 `|| true`（严格模式不允许忽略失败）

3) 确认 hooks 生效：
- `git config core.hooksPath` 应该指向 `.husky/_`
- husky runner 能找到 `.husky/<hookname>`

4) 增加 CI workflows（`.github/workflows/*.yml`）并加路径过滤

5) 保护 main：在 GitHub Settings → Branch protection rules：
- require status checks
- require pull request

---

## 7. 你真正要记住的一句话

以后你只做：`git add` → `git commit` → `git push`。
其它（格式/规范/测试/CI）都由 hooks + CI 自动挡住。
