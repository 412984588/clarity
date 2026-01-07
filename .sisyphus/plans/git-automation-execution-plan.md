# Git 自动化执行计划（严格版 / 安全版二选一）

> 你要的目标：你尽量少管事，所有规范步骤自动化；我/执行器负责实现、跑验证、提交、推送
>
> **重要现实约束（已确认）**：本仓库 Git hook 入口是 Husky：`.git/config` 中 `core.hooksPath = .husky/_`
>
> - 结论：任何 hook 必须落在 `.husky/*`（并配套 `.husky/_/*` 路由），写到 `.git/hooks/*` 不会触发
>
> 规范来源文件：`GIT-AUTOMATION-SPEC.md`（仓库根目录）

---

## 1. 我建议的默认策略（给“不想管也不懂风险”的你）

你贴的 `GIT-AUTOMATION-SPEC.md` 里包含 **post-commit 自动 push + amend + force-with-lease**。

这在业界属于高风险模式（容易把不该公开的内容立刻推上远端、会改写历史、遇到失败更难恢复）。

所以我给你两个选项：

### 选项 A（推荐默认）：严格但安全（最少麻烦）
- `pre-commit`：自动格式化 + 安全扫描 + lint（失败就不让 commit）
- `commit-msg`：强制 Conventional Commit（失败就不让 commit）
- `pre-push`：强制测试/类型检查/构建（失败就不让 push）
- CI（GitHub Actions）：远端最终兜底（不可绕过）
- **不做 post-commit 自动 push/amend/force**

你日常只需要：我/执行器把代码写好后，我来提交+推送；你不用记命令。

### 选项 B（严格照抄规范）：全自动（含 post-commit 自动 push + PROGRESS + amend + force-with-lease）
- 完全按照 `GIT-AUTOMATION-SPEC.md` 实现
- 但必须加“防递归/防 rebase/merge”护栏，否则会死循环或污染历史

> 你刚才说“看不懂风险、但我要完全照着做”，那就走 **选项 B**。

---

## 2. 成功标准（必须可验证）

### 功能（Pass/Fail）
1) `git commit` 前：pre-commit 自动跑
   - 检测合并冲突标记 / 私钥片段 / 大文件（>500KB）
   - 自动格式化（prettier/markdownlint 等）
   - lint-staged/ruff/mypy 等
   - 任一失败：commit 必须被拦截

2) `git commit` 时：commit-msg 校验
   - 不符合 `type(scope): subject`：commit 必须被拦截

3) `git push` 前：pre-push 强制测试
   - 后端：pytest + coverage gate（85%）
   - web：tsc + lint + build（严格）
   - mobile：lint +（可选 tsc）
   - 任一失败：push 必须被拦截

4) CI：push/PR 后自动运行
   - backend/web/mobile 都有 workflow 且路径正确

### 证据
- `git config --get core.hooksPath` 输出是 `.husky/_`
- 关键 hook 文件存在：`.husky/pre-commit`、`.husky/commit-msg`、`.husky/pre-push`（以及选项 B 的 `.husky/post-commit`）
- GitHub Actions 能看到对应 workflow 正常触发

---

## 3. 仓库现状（已扫描确认）

### 3.1 已存在且生效（Husky）
- `.husky/pre-commit`：已实现 staged 安全检查 + 子项目检查（严格失败）
- `.husky/commit-msg`：已复用 `solacore-api/scripts/check-commit-msg.py`
- `.husky/pre-push`：已实现后端覆盖率门槛 + web typecheck/lint + mobile lint

### 3.2 与规范文档的差距
- 规范写的是 `.git/hooks/post-commit`，但本仓库 hook 入口是 Husky，所以需要实现 `.husky/post-commit`
- `GIT-AUTOMATION-SPEC.md` 写的“Pre-commit hooks 配置（.pre-commit-config.yaml）”在本仓库目前是 **后端子项目**里有（`solacore-api/.pre-commit-config.yaml`），根目录没有
- CI：
  - backend 有 `.github/workflows/backend.yml`
  - mobile 有 `.github/workflows/mobile.yml` 但路径疑似旧目录（`clarity-mobile`）
  - web 缺 workflow

---

## 4. 执行步骤（给执行器照抄）

> 说明：执行器可以是“我”切换到执行模式，也可以是你用的另一个自动执行器。
> 你不需要懂任何细节，只要告诉执行器：按本清单逐条做，最后给我证据。

### Step 4.1（选项 B 才需要）：新增 Husky `post-commit`

新增文件：
- `.husky/post-commit`
- `.husky/_/post-commit`（两行路由文件，参考 `.husky/_/pre-commit`）

`.husky/post-commit` 逻辑（按 `GIT-AUTOMATION-SPEC.md`，但加护栏）：
1) 防递归：若 `OPENCODE_POST_COMMIT=1` 直接退出 0
2) 检测 rebase/merge 中：若存在 `.git/rebase-apply`/`.git/rebase-merge`/`.git/MERGE_HEAD`，跳过所有自动化
3) 自动 push：先 `git push origin <branch>`，失败再 `git push -u origin <branch>`
4) 更新 `docs/PROGRESS.md`：把条目插入到第一个 `---` 后面
5) `git add docs/PROGRESS.md`
6) `OPENCODE_POST_COMMIT=1 git commit --amend --no-edit --no-verify`
7) `git push --force-with-lease`

> 注意：你之前说“不要 force / 不要 amend”，那是安全版；选项 B 就必须按规范做（含 amend + force-with-lease）

### Step 4.2：补齐根目录 `.pre-commit-config.yaml`（可选但强烈建议）

目的：把规范文档里那些通用检查（whitespace/json/yaml/merge-conflict/private-key/markdownlint/prettier）统一落地。

实现方式：
- 新增根目录 `.pre-commit-config.yaml`
- 在 `.husky/pre-commit` 最前面跑一次 `pre-commit`（如果你希望完全对齐规范）

### Step 4.3：修正/补齐 GitHub Actions

1) 修复 `.github/workflows/mobile.yml`：
- `working-directory: solacore-mobile`
- `cache-dependency-path: solacore-mobile/package-lock.json`

2) 新增 `.github/workflows/web.yml`：
- `working-directory: solacore-web`
- `npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build`

3) （可选）新增统一 `.github/workflows/ci.yml`：
- 集成 pre-commit 全量校验 + backend/web/mobile

---

## 5. 验证步骤（执行器必须跑并给证据）

## Test Plan
### Objective: 验证 hooks/CI 链路严格生效
### Prerequisites:
- 已安装依赖（poetry/npm）
- GitHub remote `origin` 可用

### Test Cases:
1. Commit-msg gate：`git commit -m "bad msg"` → 被拦截
2. Pre-commit 安全：提交包含 `<<<<<<<` 的文件 → 被拦截
3. Pre-push：故意制造测试失败 → `git push` 被拦截
4. CI：推送后 GitHub Actions 出现 backend/web/mobile 的 workflow runs
5.（选项 B）Post-commit：提交后自动 push；`docs/PROGRESS.md` 被更新并通过 amend 合并进同一 commit；随后 force-with-lease push

### Success Criteria: 全部测试用例通过

---

## 6. 你现在要我怎么做（最少操心的选择）

你只要回一句：
- “用选项 A（安全）” 或 “用选项 B（照抄规范）”

然后我会把这份计划交给执行器去落地，并在落地后给你：
- 具体修改了哪些文件
- 跑了哪些验证
- CI 链接证据
