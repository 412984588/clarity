# Git 自动化工作流落地方案（按 GIT-AUTOMATION-SPEC.md）

目标：让你“几乎不用管 Git”，你只要提出需求即可；在技术侧通过 hooks + CI 把规范强制起来

> 注意：当前仓库实际启用的是 Husky（`.git/config` 里 `core.hooksPath = .husky/_`），所以 **`.git/hooks/*` 不会生效**。因此“按文档那样做”的正确落地方式是：把对应 hook 实现在 `.husky/*`，由 Husky 触发

---

## 1. 你要的最终体验（最少你要做什么）

### 日常（你不写代码的模式）
- 你只需要说一句话："实现 X" 或 "修复 Y"
- 我完成：写代码 -> 测试 -> 提交 -> 推送（如果启用自动推送） -> 更新 `docs/PROGRESS.md`

### 当你自己要提交（仍然尽量少操作）
- 你只需：`git add -A && git commit -m "..."`
- 其余自动：pre-commit 检查 -> commit-msg 校验 -> post-commit 推送+更新文档 -> CI 再兜底

---

## 2. “push” 是什么（你刚问的）

- `git commit`：把改动保存为本地的一条“版本记录”（只在你电脑上）
- `git push`：把本地的提交“上传到 GitHub/远程仓库”，让别人也能看到

---

## 3. 现状盘点（必须先对齐，不然你以为生效但其实没跑）

### 已生效的 hook
- `git commit` 会触发 `/.husky/pre-commit`
  - `solacore-api`：`poetry run pre-commit run`（已严格，不忽略失败）
  - `solacore-web`：`npx lint-staged`（目前代码里是严格 `|| exit 1`，可以继续用）
  - `solacore-mobile`：`npx lint-staged`（同上）

### 目前缺失/不稳定的部分（需要补齐，才能做到“你说的那套全自动”）
- `commit-msg`：缺少稳定的 Husky `commit-msg`（后端有脚本，但未必会被触发）
- `pre-push`：缺少稳定的 Husky `pre-push`
- `post-commit`：缺少稳定的 Husky `post-commit`（你的规范文档要“自动 push + 更新 PROGRESS.md”）

### CI 缺口
- `solacore-api` 的 CI 是对的（`.github/workflows/backend.yml`）
- `web/mobile` 的 CI 目前存在路径漂移（`clarity-*`），需要补齐成 `solacore-*`

---

## 4. 严格策略选择（你选了 A：最严格）

为了“你不用管”，默认选择最严格：
- pre-commit：严格失败就拦截（但只做快检查，避免每次提交都跑全量测试）
- pre-push：跑重检查（后端 pytest+coverage 门槛；web 类型检查/构建；mobile 类型检查）
- CI：再跑一遍全量（保证远端最终一致）
- post-commit：按你的规范做“自动推送 + 更新 PROGRESS.md”

---

## 5. 需要实现的文件改动清单（实现者照做即可）

### 5.1 本地 hooks（Husky，单一入口）

1) 新增：`.husky/commit-msg`
- 调用后端已有 `solacore-api/scripts/check-commit-msg.py "$1"`
- 目的：强制 Conventional Commits

2) 修改：`.husky/pre-commit`
- 保持“按变更目录触发”逻辑（已经是按 staged 目录）
- 对齐 spec 的 pre-commit 内容：
  - backend：继续 `poetry run pre-commit run`（不要 `--all-files`）
  - web/mobile：继续 `lint-staged`（确保失败不被吞）
  - 额外加入“show-git-diff”提示（只提示，不阻断）

3) 新增：`.husky/pre-push`
- 对齐 spec：push 前必须跑测试/重检查
- 建议实现：
  - backend：`pytest --cov=app --cov-fail-under=85`
  - web：`npx tsc --noEmit` + `npm run build`
  - mobile：`npx tsc --noEmit`（如项目支持）

4) 新增：`.husky/post-commit`
- 完整复刻你的 GIT-AUTOMATION-SPEC：
  - 自动推送到当前分支（`git push` 或 `git push -u`）
  - 更新 `docs/PROGRESS.md` 顶部记录
  - amend 同一条 commit，并 `--force-with-lease` 推送
- 必须加防递归护栏（避免 post-commit 内再次触发 post-commit 无限循环），例如用环境变量/临时文件标记一次执行

### 5.2 CI（GitHub Actions）

5) 新增或修改：`.github/workflows/ci.yml`
- 满足你的 spec：
  - Node matrix：18/20
  - `prettier --check`
  - `npm test`
  - 有 build 就跑 build
  - 另起 job：`pre-commit run --all-files`

6) 修正现有 workflow 路径漂移
- 将 `clarity-api/**`、`clarity-mobile` 改为 `solacore-api/**`、`solacore-mobile`
- 如果旧 workflow 已无意义，移除/禁用避免重复跑

---

## 6. 验收标准（你不需要懂，只看结果）

### 本地
- 随便改一个文件然后 `git commit`：
  - 会自动跑 pre-commit 检查
  - commit message 不合规会直接被拒绝
  - commit 成功后会自动 push，并更新 `docs/PROGRESS.md`

### 推送前
- 执行 `git push`：
  - 如果任何测试/检查失败，push 会证明被拦截

### 远端
- GitHub 上会自动跑 CI
- CI 失败：PR/推送会红灯

---

## 7. 风险与回滚（你不用理解原因，只要知道有退路）

如果你觉得自动推送太“吵”，或者遇到循环/卡住：
- 回滚只需要：删除 `.husky/post-commit` 或在其中加一个总开关禁用

---

## 8. 下一步怎么做

我现在是 planner，不能直接改代码
- 你运行 `/start-work` 之后，我按本计划把 hook/CI 全部落地到仓库
