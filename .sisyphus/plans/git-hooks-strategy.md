# Git Hooks 最佳实践策略（Solacore Monorepo）

> 目标：实现“提交/推送前自动跑检查”，保证规范与稳定，同时避免把开发体验搞崩

## 1. 先回答你的问题：stop hook 会让我一直工作吗？

不会

- `stop` hook（例如 Hookify 的 `scope-check`）本质是“会话结束提醒/统计”，不会强制我无限工作
- 你感觉我“停不下来”，更多来自两点：
  - 你让我“继续”，而我按“端到端完成”原则把测试、验证跑完
  - 当前仓库钩子/工具链配置有一些“分裂”和“忽略失败”，需要梳理后才能放心改

## 2. 现状（基于已扫描到的配置）

### 2.1 真实生效的 Git hooks 入口

- `.git/config` 设置了 `core.hooksPath = .husky/_`
  - 结论：Git 实际调用的是 Husky 的 hook 目录

### 2.2 当前钩子链路

- `git commit` 触发：`/.husky/pre-commit`
  - `solacore-api`：`poetry run pre-commit run --all-files`（很重）
  - `solacore-web`：`npx lint-staged || true`（失败被忽略）
  - `solacore-mobile`：`npx lint-staged || true`（失败被忽略）

- `commit-msg`：目前未见到 Husky 的 `/.husky/commit-msg`
  - `solacore-api/.pre-commit-config.yaml` 里定义了 `commit-msg-format`
  - 但它只有在 `pre-commit install --hook-type commit-msg` 真正安装后才生效
  - 由于 `hooksPath` 指向 Husky，单纯安装到 `.git/hooks/*` 可能被旁路

- `pre-push`：目前未见到 Husky 的 `/.husky/pre-push`
  - `solacore-api/.pre-commit-config.yaml` 里定义了 `pytest-coverage`（pre-push）
  - 同样存在“安装到 `.git/hooks` 但被 hooksPath 旁路”的风险

### 2.3 风险点

- **Web/Mobile hook 失败会被忽略**（`|| true`）→ 规范形同虚设
- **Hook 系统 split-brain**：Husky 生效，但后端 `setup-hooks.sh` 可能安装到 `.git/hooks/*`（不一定运行）
- **后端 pre-commit 每次 commit 跑 `--all-files`** → 容易让人烦到直接 `--no-verify`

## 3. 你说的“以后都要自动提交”到底怎么做才是最佳实践？

行业最佳实践结论（强烈建议遵守）：

- **不要在 git hook 里自动生成 commit（auto-commit / amend）**
  - 典型问题：递归触发、历史污染、提交内容不可预期、半成品状态

你真正想要的是：

- “我不用记流程，系统保证：**要么检查都过并按规范提交，要么不让提交/推送**”

这个目标最佳落地方式是“Gate（门禁）”，而不是“Auto-commit（自动写历史）”

## 4. 推荐策略（你说 B，我给你 B 方案）

### 方案 B：以 Husky 作为唯一入口，统一管理 commit-msg / pre-commit / pre-push

核心原则：

- **pre-commit：只做快速检查（目标 < 2-3 秒）**
  - Python：ruff/isort/mypy 等（尽量只跑 staged / changed files）
  - Web/Mobile：lint-staged（只跑 staged）

- **pre-push：跑“快的全量单测/类型检查”（目标 < 30-60 秒）**
  - Python：pytest 快速套件 + coverage gate（你已有 pre-commit config 可复用）
  - Web：`tsc --noEmit` + unit tests（如有）
  - Mobile：`tsc --noEmit`（如有）/ eslint（按项目可选）

- **commit-msg：强制 conventional commits 格式**
  - 复用现有 `solacore-api/scripts/check-commit-msg.py` 或引入 commitlint（Node）
  - 单仓推荐：优先复用现有 Python 脚本（避免新增 node 依赖链）

### 你现有工具链最小改动点（B 方案）

1) `/.husky/pre-commit`
- 移除 `|| true`，让 web/mobile 失败能阻止提交
- 后端不要 `--all-files`，改为：
  - `poetry run pre-commit run`（staged files）
  - 或在 `.pre-commit-config.yaml` 加 `files:` 过滤，仅对 `^solacore-api/` 生效

2) 新增 `/.husky/commit-msg`
- 调用 `solacore-api/scripts/check-commit-msg.py "$1"`（或用 pre-commit hook stage）

3) 新增 `/.husky/pre-push`
- 统一跑：
  - `solacore-api`：pytest + coverage gate（可直接调用 `poetry run pre-commit run --hook-stage pre-push`）
  - `solacore-web`：`npx tsc --noEmit` +（如有）`npm test`
  - `solacore-mobile`：`npx tsc --noEmit`（如无脚本先补）

4) 统一安装入口
- 把后端的 `solacore-api/scripts/setup-hooks.sh` 作为“安装 pre-commit hooks 的工具”保留
- 但要明确：以 Husky hooksPath 为准，不要再宣传 `.git/hooks` 为唯一入口

## 5. 规范提交的“最佳体验”建议（非强制）

- **新增一个统一命令**（不是 hook 自动 commit）
  - `scripts/commit`：
    1) 跑格式化/修复（可选）
    2) `git diff` 检查是否有自动修改，提示用户 review
    3) 跑快速测试
    4) 再执行 `git commit ...`
  - 这样你“不懂流程也能一键正确提交”，又不会污染历史

- **conventional commits 辅助输入**
  - 如果团队里很多人不熟格式，才考虑 commitizen/commitlint

## 6. 交付标准（Done Definition）

- `git commit`：
  - API/Web/Mobile 任一检查失败 → commit 被拒
  - commit message 不符合格式 → commit 被拒

- `git push`：
  - 后端 pytest + coverage gate 失败 → push 被拒
  - web ts 类型检查失败 → push 被拒

- CI：仍然跑全量（作为最后防线）

## 7. 执行清单（给实现者 /start-work 用）

1. 创建/更新 `/.husky/commit-msg`、`/.husky/pre-push`
2. 调整 `/.husky/pre-commit`：去掉 `|| true`，并对后端去掉 `--all-files`
3. 在 `solacore-api/.pre-commit-config.yaml` 增加 `files:` 过滤（只对 solacore-api 生效）
4. 补齐 Web/Mobile 的 typecheck/test 脚本（如果缺失）
5. 验证：
   - 制造一个 lint 失败的 staged 文件，确认 commit 会被挡
   - 制造一个不合规 commit message，确认 commit 会被挡
   - 制造一个后端测试失败，确认 push 会被挡

---

> 我是 planner，这里只给策略和可执行清单
> 你要我真正去改 hook、落地脚本的话，跑 `/start-work` 我再开始实施
