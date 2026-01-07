# Strict Git Hooks + “Auto Commit” Strategy (Solacore Monorepo)

> 目标：你不需要懂细节，只要按流程用 git；任何不合规的提交/推送都会被拦截。
> 说明：**不建议**用 hook “自动帮你 commit”（会递归/污染历史/难排查）。最佳实践是：
> - Hooks 负责“卡口（gatekeeping）”
> - 需要“自动化提交”时，用“单一入口命令/脚本/AI指令”在 commit 之前跑完所有检查，然后**再**由人/AI执行 commit

---

## 1) 现状扫描结论（你现在的仓库）

- Git 实际使用的 hooks 入口：`.git/config` 里 `core.hooksPath = .husky/_`
- 真实 hook 脚本在仓库根目录 `.husky/` 下（例如 `.husky/pre-commit`）
- 当前风险点：`.husky/pre-commit` 对 `solacore-web` / `solacore-mobile` 用了 `|| true`，也就是 **前端/移动端检查失败也照样允许提交**
- 后端（`solacore-api`）有一套 Python `pre-commit` 框架配置：`solacore-api/.pre-commit-config.yaml`
  - 其中定义了：
    - `pre-commit`：ruff-format/ruff/isort 等
    - `commit-msg`：`scripts/check-commit-msg.py`
    - `pre-push`：`pytest --cov-fail-under=85`
  - 但这些 **只有在对应 hook 类型被安装/被 Husky 调用** 时才一定生效

---

## 2) “严格但可用”的默认策略（我替你选）

你说你不懂选项，但想“符合规范”。这里给一个行业通用、且最不容易让人绕过的默认：

### 默认选择（推荐）

1) `pre-commit` 后端是否 `--all-files`：**B（只对 staged/相关文件）**
- 理由：全量跑太慢，会逼人用 `--no-verify` 绕过，反而“不严格”
- 全量检查建议放到 CI（GitHub Actions）或 pre-push/夜间任务

2) `pre-push` Web 是否强制 `npm run build`：**B（不强制 build，跑 tsc + 必要测试/检查）**
- 理由：Next build 经常偏慢，作为本地 pre-push 卡口容易造成“推送困难”，开发者会关 hooks
- CI 里强制 build 更稳定

3) `pre-push` Mobile 是否强制 `tsc`：**A（强制 tsc）**
- 理由：TypeScript 类型错误最常见也最致命，且通常比 build 快

### 关键原则（决定“严格”是否真的严格）

- **Hook 一旦执行，就必须失败即拦截（fail closed）**：
  - 禁止 `|| true` 这种吞错误
- **只对“本次改动涉及的子项目”执行对应检查**：
  - 避免每次提交都跑全仓库检查导致极慢

---

## 3) 需要新增/修改的 Hook 文件（实施清单）

> 说明：这里列的是“应该改哪里/加什么”，由实现者按此修改

### 3.1 必改：`.husky/pre-commit`

目标：
- 移除 `|| true`
- 仅当 staged 变更触及对应子目录才运行该子项目检查

建议逻辑（伪代码）：
- `git diff --cached --name-only` 检测是否包含 `solacore-api/`、`solacore-web/`、`solacore-mobile/`
- 若包含：进入对应目录运行检查；任何失败直接 `exit 1`

### 3.2 新增：`.husky/commit-msg`

目标：
- 强制提交信息符合规范（Conventional Commits 变体）

两种做法：
- **优先用现成的** `solacore-api/scripts/check-commit-msg.py`（无需新增依赖）
- 或引入 `commitlint`（更标准，但要加 Node 依赖与配置）

默认推荐：先用现成脚本（更少变更、风险更低）

### 3.3 新增：`.husky/pre-push`

目标（严格卡口）：
- 后端：`pytest --cov-fail-under=85`（或调用 `pre-commit` 的 `pre-push` stage）
- Web：`tsc --noEmit`（可选再跑 unit test）
- Mobile：`tsc --noEmit`

执行策略：
- 仍然只在对应子目录有改动时才运行
- 任一检查失败：阻止 push

---

## 4) 你要的“自动帮你提交”怎么做才算最佳实践

**结论：不要在 Git hooks 里做自动 commit**。原因：
- 会触发递归（hook 里再 commit -> hook 再触发）
- 会产生“你没看过但被提交”的代码（历史不可控）
- 出错时难以恢复和追踪

### 替代方案（真正可靠）

A. **由 AI/脚本作为唯一入口执行提交**（推荐）
- 你只需要说：
  - “帮我提交这次改动，按最严格流程”
- 实现者流程（自动）：
  1) `git status` 确认范围
  2) 跑与变更相关的检查（同 hooks）
  3) 生成合规 commit message（或要求你确认）
  4) `git add` + `git commit`
  5) （可选）`git push`

B. **提供一个 commit wrapper 脚本**（例如 `scripts/commit.sh`）
- 你执行一个命令，它会先跑检查再 commit
- 仍然保留 hooks 作为兜底

---

## 5) 严格提交执行手册（你只要照做）

你只需要记住 2 个动作：

1) 提交：
- `git commit -m "fix(api): ..."`
- 如果提交信息不合规：系统会提示并阻止，你只要按提示改 message

2) 推送：
- `git push`
- 如果测试/类型检查不通过：系统会阻止 push，你只需要修复后再 push

> 额外说明：你的目标是“不会有坏代码/坏提交进入远端”，所以宁可让 push 更严格，而不是让 commit 变得超慢

---

## 6) 你问的：是不是 stop hook 让 AI 一直工作？

不是。
- `scope-check` 属于 **stop event 的提醒**（warn），不会强制“AI必须继续工作”，只是提示你收尾检查
- 真正会拦截提交/推送的是 git hooks（pre-commit / commit-msg / pre-push）

---

## 7) 下一步（交接给实现者）

- 你说：`/start-work`
- 实现者按本计划落地：
  - 改 `.husky/pre-commit`（去掉 `|| true` + 按目录变更触发）
  - 加 `.husky/commit-msg`
  - 加 `.husky/pre-push`
  - 验证：分别在 api/web/mobile 改一个文件，确认 commit/push 会被严格拦截
