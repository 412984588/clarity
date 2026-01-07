# 严格但低干预：Hooks + CI + 自动提交（实施计划）

> 目标：让你“几乎不用管”，但仍然按最严格规范工作
> 
> 重要原则：
> - **不在 hook 里做 auto-commit / auto-amend**（会递归、会产生“你没看过的提交”，业界普遍认为是反模式）
> - 严格通过 **Gatekeeping** 实现：不通过就不让 commit/push
> - 真正的“全自动”放到 **CI**（远端是最终裁判）

---

## 0. 你现在仓库的真实现状（已确认）

- Git 入口 hook 由 Husky 接管：`.git/config` 设置了 `core.hooksPath = .husky/_`
- 已存在并生效的 hook 脚本：`.husky/pre-commit`
- 目前风险点：旧版本 `.husky/pre-commit` 对 web/mobile 用了 `|| true`，即 **失败也放行**（已被计划修正为严格）
- 后端已有 Python `pre-commit` 框架配置：`solacore-api/.pre-commit-config.yaml`
  - 包含 `commit-msg`（提交信息校验）与 `pre-push`（pytest+coverage）规则
  - 但这两类 hook 是否真正生效，取决于是否被安装/被 Husky 接入

---

## 1. 你的诉求翻译成“严格策略”

你想要：
- 你不需要决定 A/B 开关
- 提交前自动完成检查
- 不通过就禁止提交/推送
- 尽量少让你手动跑命令

我采用的默认策略（兼顾严格与可用）：

### 1.1 `pre-commit`（快速、只跑相关子项目）
- **后端**：`poetry run pre-commit run`（不使用 `--all-files`，只针对 staged/changed files）
- **web/mobile**：`lint-staged`（只作用 staged 文件）
- **严格**：任何一步失败 → 直接阻止 commit

理由：
- `--all-files` 在 monorepo 中会显著拖慢提交，最终逼着人用 `--no-verify`（反而更不严格）

### 1.2 `commit-msg`（强制 Conventional Commit）
- 使用后端现成脚本：`solacore-api/scripts/check-commit-msg.py`
- 任何不符合 `type(scope): subject` → 直接阻止 commit

### 1.3 `pre-push`（推送前重检查，严格阻断）
- **后端**：跑完整 pytest + 覆盖率门槛（>=85%）
- **web**：`npx tsc --noEmit` + `npm run lint`（不强制 build，build 交给 CI）
- **mobile**：`npm run lint` + `npx tsc --noEmit`（如果 mobile 项目不支持 tsc 再降级）

理由：
- 在 hook 里做 `npm run build` 往往很慢、易卡住开发节奏；最严格的 build 应该在 CI（不会被本地环境差异影响）

### 1.4 CI（最终强制）
- 每次 PR / push：
  - 后端：ruff/format/mypy/pytest+cov gate
  - web：lint/tsc/build
  - mobile：lint/tsc
  - 可选：安全扫描（依赖审计/secret scan）

---

## 2. “stop hook 会让我一直工作吗？”

不会
- 你看到的 `stop hook`（类似 scope-check）是 **提示/告警模板**，它不会让系统“循环干活”
- 真正会阻断流程的是 **Git hook exit code**（返回非 0 才会阻止 commit/push）

---

## 3. 需要变更的文件（精确到路径）

> 这些是实现侧要改的地方，我这里只列清单与目标内容，后续用 `/start-work` 让执行器落地

### 3.1 Husky 入口（保持 repo 现状：hooksPath = `.husky/_`）
- `.husky/_/pre-commit`：确保存在且内容为
  - `#!/usr/bin/env sh`
  - `. "$(dirname "$0")/h"`
- `.husky/_/commit-msg`：同上
- `.husky/_/pre-push`：同上

说明：Husky v9 的 runner 会从 `.husky/_/<hook>` 跳到 `.husky/<hook>`

### 3.2 项目 hook 脚本（真正逻辑写在这里）
- `.husky/pre-commit`
  - 只在 staged 中检测到 `solacore-api/` 才跑后端 pre-commit
  - 只在 staged 中检测到 `solacore-web/` 才跑 web lint-staged
  - 只在 staged 中检测到 `solacore-mobile/` 才跑 mobile lint-staged
  - **禁止 `|| true`**（严格不放行）
- `.husky/commit-msg`
  - `python3 solacore-api/scripts/check-commit-msg.py "$1"`
- `.husky/pre-push`
  - 根据 diff 范围（优先 `origin/main...HEAD`，否则 `HEAD~1...HEAD`）判断影响子项目
  - 对应子项目跑对应重检查
  - 失败则 exit 1 阻止 push

### 3.3 GitHub Actions（新增或完善）
- `.github/workflows/api.yml`（或统一 `ci.yml`）：后端 lint/type/test/cov
- `.github/workflows/web.yml`：web lint/tsc/build
- `.github/workflows/mobile.yml`：mobile lint/tsc
- 缓存：
  - Python：poetry cache + pre-commit cache
  - Node：npm cache

---

## 4. “全自动不用我管”能到什么程度？

在不做危险 auto-commit 的前提下，你的日常只需要：
- `git add ...`
- `git commit -m "type(scope): subject"`
- `git push`

其余都自动：
- commit 时自动跑 `pre-commit`
- commit-msg 自动校验
- push 时自动跑 `pre-push`
- push 后 CI 自动再跑一遍（最终裁判）

如果你连 commit message 都不想写：
- 可选加一条“交互式提交”命令（commitizen/脚本），但这属于额外增强，不是必须

---

## 5. 执行顺序（给执行器 /start-work 用）

1) 校验当前 hooksPath 与 Husky runner 文件是否齐全（`.husky/_/*`）
2) 修正 `.husky/pre-commit`：
   - 去掉 `--all-files`
   - 去掉 `|| true`
   - 加 staged 范围检测，仅对相关子项目运行
3) 新增 `.husky/commit-msg`（复用后端脚本）
4) 新增 `.husky/pre-push`（后端 pytest+cov gate + web tsc+lint + mobile lint+tsc）
5) 新增/修订 `.github/workflows/*`（CI 作为最终裁判）
6) 本地验证：
   - 故意制造不合规提交信息 → 应阻止 commit
   - 故意制造 lint 失败 → 应阻止 commit
7) 生成规范 commit（不 push，等你确认后再 push）

---

## 6. 我会用中文输出进度（你能看懂）

执行阶段我会按这种节奏汇报：
- “我正在检查哪些文件/规则”
- “这一步通过/失败原因是什么”
- “下一步要做什么”

---

## 7. 转交执行

我现在是 planner（只出方案）

请你运行：`/start-work`
- 执行器会按本计划把 hook/CI 改完，并按规范生成 commit（默认不 push，除非你明确允许）
