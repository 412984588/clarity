#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 用法提示
usage() {
    echo -e "${BLUE}用法:${NC} $0 <branch> \"<title>\" \"<body>\" [--force]"
    echo ""
    echo "参数:"
    echo "  branch   分支名 (如 fix/ci-green)"
    echo "  title    PR 标题 (如 \"fix: resolve CI issue\")"
    echo "  body     PR 描述"
    echo "  --force  强制重置到 origin/main (危险操作)"
    echo ""
    echo "示例:"
    echo "  $0 fix/example \"chore: example\" \"example body\""
    exit 1
}

# 检查参数
if [ $# -lt 3 ]; then
    usage
fi

BRANCH="$1"
TITLE="$2"
BODY="$3"
FORCE="${4:-}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Git/PR 自动化管家${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 0: 检查 gh 登录状态
echo -e "${YELLOW}[0/8] 检查 GitHub CLI 登录状态...${NC}"
if ! gh auth status &>/dev/null; then
    echo -e "${RED}未登录 GitHub CLI${NC}"
    echo -e "请运行: ${GREEN}gh auth login${NC}"
    echo -e "或访问: ${GREEN}https://github.com/login/device${NC} 输入设备码"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI 已登录${NC}"

# Step 1: 检查工作区状态
echo ""
echo -e "${YELLOW}[1/8] 检查工作区状态...${NC}"
git fetch origin

if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠ 工作区有未提交的改动:${NC}"
    git status --short

    if [ "$FORCE" == "--force" ]; then
        echo -e "${RED}--force 模式: 重置到 origin/main...${NC}"
        git reset --hard origin/main
        git clean -fd
        echo -e "${GREEN}✓ 已重置${NC}"
    else
        echo ""
        echo -e "${YELLOW}选项:${NC}"
        echo "  1) 继续 (将这些改动包含在 PR 中)"
        echo "  2) 退出 (手动处理后重新运行)"
        echo "  3) 强制重置 (丢弃所有改动)"
        read -p "请选择 [1/2/3]: " choice

        case $choice in
            1) echo -e "${GREEN}继续...${NC}" ;;
            2) echo -e "${YELLOW}已退出${NC}"; exit 0 ;;
            3)
                git reset --hard origin/main
                git clean -fd
                echo -e "${GREEN}✓ 已重置${NC}"
                ;;
            *) echo -e "${RED}无效选择${NC}"; exit 1 ;;
        esac
    fi
else
    echo -e "${GREEN}✓ 工作区干净${NC}"
fi

# Step 2: 创建或切换分支
echo ""
echo -e "${YELLOW}[2/8] 切换到分支: ${BRANCH}${NC}"
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" == "$BRANCH" ]; then
    echo -e "${GREEN}✓ 已在目标分支${NC}"
elif git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git switch "$BRANCH"
    echo -e "${GREEN}✓ 切换到已存在的分支${NC}"
else
    git switch -c "$BRANCH"
    echo -e "${GREEN}✓ 创建新分支${NC}"
fi

# Step 3: 暂存所有改动
echo ""
echo -e "${YELLOW}[3/8] 暂存改动...${NC}"
git add -A

if [ -z "$(git diff --cached --name-only)" ]; then
    echo -e "${YELLOW}⚠ 没有改动需要提交${NC}"
    echo -e "如果只是想创建空 PR，请先做一些修改"
    exit 1
fi

echo -e "${GREEN}✓ 已暂存:${NC}"
git diff --cached --stat | head -10

# Step 4: 提交
echo ""
echo -e "${YELLOW}[4/8] 提交: ${TITLE}${NC}"
git commit -m "$TITLE"
echo -e "${GREEN}✓ 已提交${NC}"

# Step 5: 推送
echo ""
echo -e "${YELLOW}[5/8] 推送到 origin/${BRANCH}...${NC}"
git push -u origin "$BRANCH"
echo -e "${GREEN}✓ 已推送${NC}"

# Step 6: 创建 PR
echo ""
echo -e "${YELLOW}[6/8] 创建 PR...${NC}"
unset GITHUB_TOKEN
PR_URL=$(gh pr create --base main --head "$BRANCH" --title "$TITLE" --body "$BODY" 2>&1)

if echo "$PR_URL" | grep -q "already exists"; then
    echo -e "${YELLOW}⚠ PR 已存在，获取现有 PR...${NC}"
    PR_URL=$(gh pr view "$BRANCH" --json url -q .url)
fi

echo -e "${GREEN}✓ PR: ${PR_URL}${NC}"

# Step 7: 设置自动合并
echo ""
echo -e "${YELLOW}[7/8] 设置自动合并 (squash)...${NC}"
unset GITHUB_TOKEN
gh pr merge --auto --squash --delete-branch

echo -e "${GREEN}✓ 已设置自动合并${NC}"

# Step 8: 等待 CI 并同步
echo ""
echo -e "${YELLOW}[8/8] 等待 CI 完成并同步 main...${NC}"
echo -e "${BLUE}监控 CI 状态 (Ctrl+C 可中断)...${NC}"

# 提取 PR 编号
PR_NUM=$(echo "$PR_URL" | grep -oE '[0-9]+$')

# 等待 PR 合并
MAX_WAIT=300
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    STATE=$(gh pr view "$PR_NUM" --json state -q .state 2>/dev/null || echo "UNKNOWN")

    if [ "$STATE" == "MERGED" ]; then
        echo -e "${GREEN}✓ PR 已合并!${NC}"
        break
    elif [ "$STATE" == "CLOSED" ]; then
        echo -e "${RED}✗ PR 已关闭 (未合并)${NC}"
        exit 1
    fi

    echo -ne "\r等待中... ${WAIT_TIME}s (状态: $STATE)  "
    sleep 10
    WAIT_TIME=$((WAIT_TIME + 10))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo -e "${YELLOW}⚠ 等待超时，请手动检查 PR 状态${NC}"
    echo -e "PR: $PR_URL"
    exit 0
fi

# 同步 main
echo ""
echo -e "${YELLOW}同步本地 main...${NC}"
git switch main
git pull --ff-only
git branch -d "$BRANCH" 2>/dev/null || true

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "PR: ${PR_URL}"
echo -e "Main commit: $(git log --oneline -1)"
echo -e "工作区: $(git status --short || echo '干净')"
