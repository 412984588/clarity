# Git 自动化（严格 + 少操心）落地方案（OpenCode / 本仓库适配）

> 目标：你不需要记命令、不需要懂 Git。
> 你只要“告诉我做什么”，执行器会：写代码 → 跑测试 → 通过才提交 → 自动推送 GitHub → 自动更新 `docs/PROGRESS.md`。
>
> 关键约束：本仓库 Git 配置 `core.hooksPath = .husky/_`，所以 **必须用 Husky 作为唯一 hook 入口**。

---

## 0. 先定位你截图里那份规范文件

- 规范文件实际路径：`docs/GIT-AUTOMATION-SPEC.md`
- 这份文档描述的是一种“commit 后自动 push + 自动更新 PROGRESS.md”的工作流

---

## 1. 现状盘点（基于代码库扫描）

### 1.1 当前真实生效的 hook 入口
- `.git/config`：`hooksPath = .husky/_`
- Husky 路由器：`.husky/_/h` + `.husky/_/husky.sh`

### 1.2 已存在的 hooks（已实现/已在仓库里）
- `.husky/pre-commit`：已是“严格版”（不吞错），并且会做 staged 安全检查
- `.husky/commit-msg`：已调用 `solacore-api/scripts/check-commit-msg.py`，强制 Conventional Commits
- `.husky/pre-push`：已跑重校验（API pytest+coverage gate 85%，Web tsc+lint，Mobile lint）

### 1.3 仍缺口/不一致
- **缺少 `.husky/post-commit`**：所以“commit 后自动 push + 自动更新 `docs/PROGRESS.md`”目前不是完整链路
- **Mobile CI 路径错**：`.github/workflows/mobile.yml` 仍使用 `clarity-mobile`，实际目录是 `solacore-mobile`
- **缺少 Web CI**：没有对 `solacore-web` 的 GitHub Actions workflow（lint/tsc/build）

---

## 2. 严格自动化的核心策略（照抄 Claude Code 全局设定 + 业内最佳实践）

### 2.1 “最严格”意味着什么（可执行定义）
- **commit 必须合规**：不合规直接拒绝（commit-msg gate）
- **commit 前必须检查**：格式化/静态检查/安全扫描（pre-commit gate）
- **push 前必须跑重测试**：失败就不允许推送（pre-push gate）
- **远端最终兜底**：GitHub Actions 必须能跑并能阻止坏代码合入

### 2.2 你要的“我不管，全部自动完成”怎么实现
- 你平时只需要：一句话告诉我需求
- 执行器会自动：改代码 + 跑测试 + 合规 commit + 自动 push
- Hook/CI 是“硬闸门”：任何一步失败都会阻止进入下一步

---

## 3. 实施改动清单（执行器照抄）

### 3.1 补齐 Husky `post-commit`
**新增：**
- `.husky/post-commit`
- `.husky/_/post-commit`（两行路由文件：`#!/usr/bin/env sh` + `. "$(dirname "$0")/h"`）

**`post-commit` 要做的事（按你要求：全自动 + 严格 + 少风险）**
1. 自动 push 到 `origin/<当前分支>`
2. 自动更新 `docs/PROGRESS.md`
3. 把 `docs/PROGRESS.md` 更新单独做成 **新 commit**（不要 amend，不要 force push）
   - 你说的“更安全”版本：会产生 2 个 commits（功能提交 + progress 提交），但历史更稳定

**必须加的安全护栏（防死循环/防事故）**
- 防递归：环境变量（例如 `OPENCODE_POST_COMMIT=1`）
  - 如果变量存在：立即 exit 0
  - 在脚本内部做 progress commit 时设置该变量，避免再次触发
- 如果处于 rebase/merge：跳过 PROGRESS 更新（避免破坏 git 状态）
- 如果没有 origin：打印提示并 exit 0

### 3.2 修复/补齐 GitHub Actions（远端兜底）
1. 修改 `.github/workflows/mobile.yml`
   - `working-directory: solacore-mobile`
   - `cache-dependency-path: solacore-mobile/package-lock.json`
2. 新增 `.github/workflows/web.yml`
   - `working-directory: solacore-web`
   - `npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`
3. （可选但推荐）新增 `.github/workflows/ci.yml`
   - job1：`pre-commit run --all-files`（Python + pre-commit）
   - job2：backend（ruff/mypy/pytest）
   - job3：web（lint/tsc/build）
   - job4：mobile（lint/tsc）

> 注意：目前已有 `backend.yml`，可以先不删，等 `ci.yml` 稳定后再收敛

---

## 4. 验证与证据（执行器必须输出）

### 4.1 本地验证（必须）
1. `git config --get core.hooksPath` 输出应为 `.husky/_`
2. `ls -la .husky/post-commit .husky/_/post-commit`（确认存在且可执行）
3. 触发链路演练（在临时分支）
   - 提交一个合法 commit
   - 观察终端：pre-commit → commit-msg → post-commit（push + PROGRESS 更新）
   - 最终 `git status` 必须干净
   - `git log -2` 必须看到：功能 commit + progress commit

### 4.2 远端验证（必须）
- 推送后在 GitHub Actions UI 看到：backend + web + mobile workflows 都触发并运行

---

## 5. 你要的最终使用方式（不需要记任何命令）

- 你只需要用中文告诉我：
  - “修复登录” / “加一个按钮” / “帮我把移动端登录对齐后端”
- 我会自动：实现 → 自测 → 按规范提交 → 自动推送 → 记录进度

---

## 6. 备注：为什么不按旧文档里的 force-with-lease / amend

- 业内最佳实践与风险评估：`post-commit` 里 `--amend` + `--force-with-lease` 风险更高
- 你刚才也确认要“更安全”：
  - 不 amend
  - 不 force push
  - 用新 commit 记录 PROGRESS
- 本计划按“更安全但仍全自动”的版本落地
