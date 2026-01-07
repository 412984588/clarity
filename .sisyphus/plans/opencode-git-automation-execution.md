# OpenCode Git 自动化执行计划（严格版，对齐 `GIT-AUTOMATION-SPEC.md`）

> 你想要的体验：你不用懂 Git、不用记命令；你只管“提需求”，我（执行器）负责：写代码→跑测试→按规范提交→自动推送→自动更新进度。
>
> 本文件是交付给执行器的“照抄清单”：实现时严格按步骤修改、跑验证、输出证据。

---

## 0. 关键事实（执行前确认）

- 本仓库 Git 实际 hook 入口：`.git/config` 里 `core.hooksPath = .husky/_`
  - 结论：**必须用 Husky 体系实现 hooks**（`.husky/<hook>` + `.husky/_/<hook>`），不能再依赖 `.git/hooks/*`

- 现有 hook 状态（以当前工作区为准）：
  - 已存在：`.husky/pre-commit`（已做 staged 安全检查 + 子项目 gate）
  - 已存在但需纳入 git：`.husky/commit-msg`、`.husky/pre-push`（当前是 untracked，需要 `git add`）
  - 缺失：`.husky/post-commit` + `.husky/_/post-commit`

- CI 状态：
  - 已有：`.github/workflows/backend.yml`
  - mobile workflow 路径疑似旧目录：`.github/workflows/mobile.yml` 指向 `clarity-mobile`（需要改为 `solacore-mobile`）
  - web workflow 缺失：需要新增 `.github/workflows/web.yml`

---

## 1. 成功标准（Pass/Fail）

### 1.1 本地链路
1. `git commit` 前：Pre-commit 自动运行
   - 自动检查：合并冲突标记 / 私钥片段 / 大文件 / staged diff 提醒
   - 子项目检查：API/web/mobile 仅在对应目录有 staged 变更时运行
   - 任意失败：**必须阻止 commit**（exit code != 0）

2. `git commit` 时：Commit message 强制 `type(scope): subject`
   - 不合规：**必须阻止 commit**

3. `git commit` 成功后：Post-commit 自动运行
   - 自动 push 到 `origin/<当前分支>`
   - 自动更新 `docs/PROGRESS.md`
   - 按规范：更新后执行 `--amend` 并 `--force-with-lease` 推送
   - 必须有防递归保护（否则会无限循环）

4. `git push` 前：Pre-push 自动运行
   - API：pytest + coverage gate（85%）
   - Web：tsc + lint（严格）
   - Mobile：lint（可再加 tsc，见 4.2）
   - 任意失败：**必须阻止 push**

### 1.2 远程链路（CI 兜底）
- push/PR 触发 GitHub Actions：backend + web + mobile 都要跑

---

## 2. 实施步骤（严格按顺序执行）

### Step 2.1 新增 Husky `post-commit`（按规范实现“自动 push + PROGRESS 更新 + amend + force-with-lease”）

**新增文件 1**：`.husky/post-commit`
- 行为：
  1) 递归保护：如果 `OPENCODE_POST_COMMIT=1` → 直接 `exit 0`
  2) 检查是否处于 rebase/merge（存在 `.git/rebase-apply` / `.git/rebase-merge` / `.git/MERGE_HEAD`）
     - 若是：打印提示，跳过自动 amend/push（避免破坏 rebase）
  3) 获取当前分支：`BRANCH=$(git branch --show-current)`
  4) push：优先 `git push origin "$BRANCH"`；失败再尝试 `git push -u origin "$BRANCH"`
  5) 更新 `docs/PROGRESS.md`（如果文件存在）：
     - 插入到第一个 `---` 之后（保持原文结构）
     - 插入内容（参考 `GIT-AUTOMATION-SPEC.md`）：
       - `### [YYYY-MM-DD HH:MM] - 自动提交`
       - `- [x] **完成**: <commit message>`
       - `- [x] **测试**: 通过 ✅`
       - `- [x] **推送**: 完成`
       - `---`
  6) `git add docs/PROGRESS.md`
  7) `export OPENCODE_POST_COMMIT=1`
  8) `git commit --amend --no-edit --no-verify`
  9) `git push origin "$BRANCH" --force-with-lease`

**新增文件 2**：`.husky/_/post-commit`
- 内容与其它路由文件一致：
  - `#!/usr/bin/env sh`
  - `. "$(dirname "$0")/h"`

**验收（本地）**：
- `git config --get core.hooksPath` 输出为 `.husky/_`
- `ls -la .husky/post-commit .husky/_/post-commit`（文件存在 + 可执行）


### Step 2.2 对齐并“严格化”现有 Husky hooks

1) `.husky/pre-commit`
- 确认：web/mobile 不存在 `|| true`（必须失败即拦截）
- 确认：已有 staged 安全检查（冲突标记/私钥/大文件）
- 建议：保留 “staged 改动概览” 输出（你不看也没关系，但会帮助避免误提交）

2) `.husky/commit-msg`
- 必须调用：`python3 solacore-api/scripts/check-commit-msg.py "$1"`

3) `.husky/pre-push`
- 保持/确认：
  - API：`pytest --cov-fail-under=85`
  - Web：`npx tsc --noEmit` + `npm run lint`
  - Mobile：`npm run lint`


### Step 2.3 CI：修复 mobile 路径 + 新增 web workflow

1) 修复：`.github/workflows/mobile.yml`
- `defaults.run.working-directory` 改为 `solacore-mobile`
- `cache-dependency-path` 改为 `solacore-mobile/package-lock.json`

2) 新增：`.github/workflows/web.yml`
- working-directory：`solacore-web`
- steps：`npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`

---

## 3. 验证计划（必须输出证据）

### 3.1 Commit message gate
- 尝试：`git commit -m "bad message"`
- 预期：被 `.husky/commit-msg` 阻止

### 3.2 Pre-commit gate（安全检查）
- staged 一个包含 `<<<<<<<` 的文件
- 预期：pre-commit 阻止提交，并打印错误

### 3.3 Post-commit 自动化
- 创建一个合法 commit
- 预期：
  - 自动 push 成功
  - `docs/PROGRESS.md` 新增记录
  - 发生 `--amend` 后再次 push（force-with-lease）
  - 不发生递归死循环（OPENCODE_POST_COMMIT 生效）

### 3.4 Pre-push gate
- `git push`
- 预期：跑测试/检查；失败则拒绝 push

### 3.5 GitHub Actions
- 在 GitHub Actions 页面能看到：backend + web + mobile workflows 都触发并运行

---

## 4. 取舍与风险（给执行器）

### 4.1 业界共识 vs 你要求
- 业界一般不推荐 `post-commit` 自动 push / amend / force-with-lease（风险：误推送、历史污染、CI 噪音）
- 你明确要求“尽量不管事 + 全自动 + 最严格”，因此按 `GIT-AUTOMATION-SPEC.md` 实现，但必须加：
  - 防递归环境变量
  - rebase/merge 检测

### 4.2 Mobile tsc 是否要加（严格程度可再加强）
- 目前 mobile `package.json` 没有 `tsc` 脚本，但可以用 `npx tsc --noEmit`
- 若执行器确认可跑，再把它加到 `.husky/pre-push`

---

## 5. 回滚方案

- 删除新增：`.husky/post-commit`、`.husky/_/post-commit`
- 恢复 `.github/workflows/mobile.yml` / 删除 `.github/workflows/web.yml`（如需要）
- 恢复 `.husky/*` 到改动前版本

