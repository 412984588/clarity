# Git 自动化落地实施方案（对齐 GIT-AUTOMATION-SPEC v1.0）

> 目标：让你**尽量少操心**，并且**严格按规范**自动化（格式/安全/提交规范/测试/CI）。
>
> 你给的规范文件路径（已找到）：`/Users/zhimingdeng/Documents/通用/GIT-AUTOMATION-SPEC.md`
>
> 说明：本计划是“落地施工单”。我不会在这里直接改代码/改 hooks。
> 你运行 `/start-work` 后，我会按此计划把所有文件改好并验证。

---

## 1) 你要的最终体验（尽量少管事）

你只需要做两步（最少可行且最稳定）：
1. `git add -A`
2. `git commit -m "..."`

然后系统自动保证：
- 提交前：格式化 + 安全检查 + 提交信息规范（不合规直接拦截）
- 推送前：自动跑测试（不通过禁止 push）
- 推送后：GitHub Actions 再跑一遍严格校验

> 解释你问的：`push` 就是“把你本地的提交上传到 GitHub”。

---

## 2) 成功标准（验收用，不需要你懂实现）

**功能性（必须）**
- 不符合提交信息格式时：`git commit` 必须失败，并提示原因
- 提交时：若格式化/安全检查发现问题，`git commit` 必须失败（并提示需要重新 `git add`）
- 推送时：如果测试失败，`git push` 必须被拦截
- CI：每次 PR / push 必须跑对应项目的 CI（backend/web/mobile）

**可观测（你能看到）**
- 终端在 commit/push 时会输出明确的“正在做什么 / 失败原因 / 下一步怎么做”

**二选一策略（严格程度）**
- 你回复了 `a`：按“最严格”执行（但会尽量用“分层”避免每次 commit 太慢）

---

## 3) 现状盘点（为什么现在没法做到规范那样）

当前仓库的真实状态（已验证）：
- Git 入口使用 Husky：`.git/config` 里 `core.hooksPath = .husky/_`
- 目前只有 `.husky/pre-commit` 是确定存在且会执行
  - `solacore-api`：会跑 `poetry run pre-commit run`
  - `solacore-web` / `solacore-mobile`：`lint-staged` 失败被 `|| true` 吞掉（不严格）
- `commit-msg` / `pre-push` **没有稳定的 Husky hook 文件**（这意味着“提交规范”和“推送前测试”未必会执行）
- CI：backend 有 `backend.yml`，但 web/mobile workflow 存在路径漂移（例如 `clarity-mobile`）

---

## 4) 落地策略（严格 + 少操心）

### 核心原则
- **单一入口**：以 Husky 为唯一本地 hooks 入口（因为当前 Git 已经 hooksPath 指向 Husky）
- **分层校验**：
  - `pre-commit`：只跑“快检查”（格式/静态检查/安全检查），保证 commit 不慢
  - `pre-push`：跑“重检查”（单测 + 覆盖率门槛 + TS typecheck），保证 push 前一定靠谱
  - GitHub Actions：再跑一遍，保证远端强一致

### 关键决策：是否做“post-commit 自动推送 + 自动 amend PROGRESS.md”
你给的规范包含 `post-commit` 自动推送和 amend。
- 业界最佳实践一般**不推荐** hook 自动推送/自动 amend（容易制造历史噪音、失败状态难恢复）
- 但你明确要求“越少管越好”，所以这里提供两个可选落地模式：

**模式 A（推荐，严格且稳定）**
- 你手动执行 `git push`（只多一步）
- 系统用 `pre-push` 严格拦截（测试不过不让 push）
- 不做 post-commit 自动 push / amend

**模式 B（完全自动，贴合你的规范）**
- `post-commit` 自动 `git push`
- 自动写入 `docs/PROGRESS.md`
- 是否 `--amend` + `--force-with-lease`：按你规范执行（最严格，但风险也最高）

> 你选了 `a`（最严格），本计划默认按 **模式 B** 做；
> 如果你觉得 push 也想手动（少一个风险），我可以切到模式 A。

---

## 5) 需要改哪些文件（施工清单）

### 5.1 Husky hooks（本地强制）
- `/.husky/pre-commit`
  - 修复：去掉 web/mobile 的 `|| true`，失败必须拦截 commit
  - 追加：加入“git diff 提醒”输出（对齐你的规范里的 show-git-diff）
  - 追加：加入安全检查（私钥/大文件/merge conflict marker）
  - 保留：按目录变更触发对应子项目检查（避免不相关目录也跑）

- `/.husky/commit-msg`
  - 新增：强制 Conventional Commit
  - 复用：`solacore-api/scripts/check-commit-msg.py "$1"`（仓库已有脚本）

- `/.husky/pre-push`
  - 新增：严格跑测试/类型检查
  - backend：`poetry run pytest ... --cov-fail-under=85`
  - web：`npx tsc --noEmit && npm run lint && npm run build`（最严格）
  - mobile：`npx tsc --noEmit`（若配置可用；否则退化为 lint）

- `/.husky/post-commit`（仅模式 B）
  - 新增：自动 push + 更新 `docs/PROGRESS.md`
  - 注意：此 hook 必须避免递归（例如用环境变量或检测是否在 hook 中运行）

### 5.2 统一的安全检查实现（对齐 GIT-AUTOMATION-SPEC）
你规范里 pre-commit hooks 使用的是 pre-commit 框架（`.pre-commit-config.yaml`）。
但当前仓库 hook 入口是 Husky（Node）。落地有两条路：

- 路线 1（最贴合规范）：在**仓库根目录新增** `.pre-commit-config.yaml`，并在 `.husky/pre-commit` 里调用：
  - `pre-commit run --hook-stage pre-commit --files <staged-files>`
  - 优点：和你规范几乎一致
  - 前提：本机安装 `pre-commit`（一次性）

- 路线 2（纯 Husky 实现）：用脚本实现等价检查（merge conflict marker / 大文件 / 私钥检测）
  - 优点：无需 python pre-commit
  - 缺点：实现成本更高

本计划默认采用 **路线 1**（最贴合你的规范）。

### 5.3 GitHub Actions（远端强制）
- 新增或修复：`.github/workflows/ci.yml`（你规范里的文件）
  - jobs:
    - `backend`: 复用现有 `backend.yml` 的逻辑或整合进 ci.yml
    - `web`: `npm ci` + `lint` + `tsc --noEmit` + `build`（Next.js）
    - `mobile`: `npm ci` + `lint` + `tsc --noEmit`
    - `pre-commit-check`: `pre-commit run --all-files`

- 清理/修正现有 workflow 的路径漂移
  - 例如把 `clarity-mobile` / `clarity-api` 的 working-directory 修正为 `solacore-mobile` / `solacore-api`

---

## 6) 具体实现细节（实现者照抄）

### 6.1 `.husky/commit-msg` 内容（模板）
```sh
#!/usr/bin/env sh
set -eu
ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$ROOT_DIR" || exit 1
python3 solacore-api/scripts/check-commit-msg.py "$1"
```

### 6.2 `.husky/pre-commit` 必改点
- 保留“按子项目变更触发”的逻辑（当前已有）
- 把：
  - `npx lint-staged || true` → `npx lint-staged || exit 1`
- 增加：
  - `echo "⚠️ 请确认：git diff --cached"`
  - 调用 `pre-commit`（根目录）对 staged 文件执行：trailing whitespace / eof / yaml/json / merge conflict / large file / private key / prettier / markdownlint

### 6.3 `.husky/pre-push`（最严格）
- backend：覆盖率门槛 85%（与 `solacore-api/.pre-commit-config.yaml` 一致）
- web：`tsc --noEmit` + `npm run lint` + `npm run build`
- mobile：`tsc --noEmit`

> 如果 mobile 没有可用 tsc 或太慢：先降级为 lint，CI 仍然强制 tsc

### 6.4 `.husky/post-commit`（模式 B）
- 自动 push 当前分支
- 更新 `docs/PROGRESS.md`
- 再 `git commit --amend --no-edit --no-verify`
- `git push --force-with-lease`

> 这里会加入“防递归锁”（比如写一个临时文件或环境变量）确保不会无限循环

---

## 7) 测试计划（落地后怎么证明生效）

### Objective
验证 commit/push/CI 的“严格闸门”全部生效

### Test Cases
1. Commit message 不合规：`git commit -m "bad message"` → 必须失败
2. 引入明显的格式问题：commit 时被自动修复并提示重新 add
3. 引入一个失败测试：`git push` 必须被拦截
4. 打开 PR：GitHub Actions 必须跑完并通过

### Success Criteria
全部测试用例通过（失败即不算完成）

---

## 8) 你需要做的（最少）

- 一次性安装依赖（我会在 /start-work 落地时帮你自动检测并给出命令）
  - `pre-commit`（如果采用路线 1）
  - Node 依赖（web/mobile 已有）

日常使用：你几乎不用想流程
- 我来写代码、跑测试、提交、推送
- 你只负责说“要做什么”

---

## 9) /start-work 执行顺序（实现者 SOP）

1. 备份当前 hooks（复制 `.husky/*` 到 `.sisyphus/backups/<timestamp>/`）
2. 落地 `.husky/commit-msg`、`.husky/pre-push`、（可选）`.husky/post-commit`
3. 修 `.husky/pre-commit`：移除 `|| true`，补齐严格检查
4. 新增根目录 `.pre-commit-config.yaml`（路线 1）并让 `.husky/pre-commit` 调用它
5. 新增/修复 `.github/workflows/ci.yml`，并修正现有 workflow 路径漂移
6. 本地验证：逐条跑 Test Cases
7. 最后：提交一次 “chore(repo): enable strict git automation” 作为落地提交

