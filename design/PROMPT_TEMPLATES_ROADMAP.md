# 🎭 AI 角色模板功能实现路线图

## 📋 功能概述

**目标用户**: 不会写提示词的普通用户
**核心价值**: 一键启用专业 AI 角色（英语老师、生活教练、旅行向导等）
**数据来源**: [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) (170+ 开源提示词)

---

## 🗓️ 实施计划（3 阶段）

### 阶段 1: 数据库 & 后端 API（2-3 天）

#### 1.1 数据库迁移
```bash
# 创建 Alembic 迁移文件
cd solacore-api
alembic revision -m "add prompt templates table"
```

**迁移内容**:
- 创建 `prompt_templates` 表（见 `design/prompt_templates_schema.sql`）
- 修改 `sessions` 表，添加 `template_id` 字段

#### 1.2 导入提示词数据
```bash
# 下载官方数据
curl -O https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv

# 生成 SQL 插入语句
python design/import_prompts_script.py prompts.csv

# 执行 SQL
psql -d solacore -f prompts_seed.sql
```

#### 1.3 实现后端 API
新增路由文件: `app/routers/templates.py`

**需要实现的端点**:
- `GET /api/v1/templates` - 获取模板列表
- `GET /api/v1/templates/{id}` - 获取单个模板详情
- `GET /api/v1/templates/popular` - 热门模板
- `POST /api/v1/sessions` - 修改创建会话逻辑，支持 `template_id`

**核心逻辑**（创建会话时自动注入提示词）:
```python
async def create_session_with_template(
    request: SessionCreateRequest,
    current_user: User,
    db: AsyncSession
):
    if request.template_id:
        # 1. 获取模板
        template = await db.get(PromptTemplate, request.template_id)

        # 2. 创建系统消息（提示词）
        system_message = Message(
            session_id=session.id,
            role="system",
            content=template.system_prompt
        )

        # 3. 添加欢迎消息
        if template.welcome_message:
            welcome_msg = Message(
                role="assistant",
                content=template.welcome_message
            )

        # 4. 更新使用次数统计
        template.usage_count += 1
```

#### 1.4 编写测试
```bash
pytest tests/test_templates.py -v
```

---

### 阶段 2: 前端 UI（2-3 天）

#### 2.1 创建模板选择页面

**页面路径**: `/create-session` 或 `/templates`

**UI 组件**:
```jsx
// components/TemplateGallery.tsx
const TemplateGallery = () => {
  const [category, setCategory] = useState('all');
  const { data: templates } = useTemplates({ category });

  return (
    <div>
      {/* 分类标签 */}
      <Tabs value={category} onChange={setCategory}>
        <Tab label="全部" value="all" />
        <Tab label="📚 学习成长" value="learning" />
        <Tab label="❤️ 生活健康" value="life" />
        <Tab label="💼 工作职场" value="work" />
        <Tab label="🎨 娱乐创意" value="entertainment" />
      </Tabs>

      {/* 模板卡片网格 */}
      <Grid container spacing={2}>
        {templates.map(template => (
          <Grid item xs={12} sm={6} md={4} key={template.id}>
            <TemplateCard
              emoji={template.icon_emoji}
              title={template.role_name_cn || template.role_name}
              description={template.description}
              usageCount={template.usage_count}
              onClick={() => createSessionWithTemplate(template.id)}
            />
          </Grid>
        ))}
      </Grid>
    </div>
  );
};
```

#### 2.2 修改会话创建流程

**原流程**:
```
点击"新建会话" → 直接创建空白会话
```

**新流程**:
```
点击"新建会话"
  ↓
显示选择器: [空白会话] [选择 AI 角色]
  ↓
选择角色 → 显示角色卡片 → 点击创建
  ↓
自动注入提示词 + 显示欢迎消息
```

#### 2.3 会话列表显示模板标识
```jsx
// SessionCard.tsx
{session.template && (
  <Chip
    icon={<span>{session.template.icon_emoji}</span>}
    label={session.template.role_name_cn}
    size="small"
  />
)}
```

---

### 阶段 3: 优化 & 推广（1-2 天）

#### 3.1 数据优化
- 根据使用统计，调整模板排序
- 添加更多中文翻译
- 优化欢迎消息，更符合国内用户习惯

#### 3.2 用户引导
- 首次使用时，展示"探索 AI 角色"引导
- 在首页推荐 3-5 个热门角色

#### 3.3 分析统计
```sql
-- 查看最受欢迎的角色
SELECT role_name, role_name_cn, usage_count
FROM prompt_templates
ORDER BY usage_count DESC
LIMIT 10;
```

---

## 📊 预期效果

### 用户体验提升
- ✅ **降低门槛**: 不懂提示词也能用专业 AI
- ✅ **提高留存**: 多种角色满足不同需求
- ✅ **增加粘性**: 用户会回来尝试不同角色

### 数据指标
- **模板使用率**: 预计 60%+ 新会话会选择模板
- **热门角色**: 英语老师、生活教练、职业顾问
- **会话时长**: 使用模板的会话平均时长更长

---

## 🎯 优先级建议

### MVP（最小可行产品）- 推荐先做 20 个角色

| 分类 | 数量 | 推荐角色 |
|------|------|----------|
| 📚 学习成长 | 5 | English Teacher, Career Counselor, Essay Writer, Note-taking, Etymologist |
| ❤️ 生活健康 | 5 | Life Coach, Mental Health Adviser, Friend, Personal Trainer, Dietitian |
| 💼 工作职场 | 5 | Resume Helper, Interviewer, Social Media Manager, Salesperson, IT Architect |
| 🎨 娱乐创意 | 5 | Storyteller, Travel Guide, Chef, Interior Decorator, Poet |

### 完整版 - 后续可扩展到 170+ 角色
包括技术类（Linux Terminal, JavaScript Console）、小众类（Astrologer, Dream Interpreter）

---

## 🔧 技术栈

- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: React + TypeScript + Material-UI
- **数据源**: awesome-chatgpt-prompts (CSV)
- **迁移工具**: Alembic

---

## 📂 相关文件

| 文件 | 说明 |
|------|------|
| `design/prompt_templates_schema.sql` | 数据库表结构 |
| `design/prompt_templates_api.md` | API 接口设计 |
| `design/import_prompts_script.py` | 数据导入脚本 |
| `design/PROMPT_TEMPLATES_ROADMAP.md` | 本文档 |

---

## 🚀 开始实施

```bash
# 1. 查看设计文档
cd /Users/zhimingdeng/Documents/claude/clarity/design

# 2. 创建数据库迁移
cd ../solacore-api
alembic revision -m "add prompt templates"

# 3. 下载并导入数据
curl -O https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv
python ../design/import_prompts_script.py prompts.csv

# 4. 运行迁移
alembic upgrade head

# 5. 实现后端 API
# 创建 app/routers/templates.py

# 6. 实现前端 UI
# 创建 components/TemplateGallery.tsx
```

---

**需要我开始实施吗？老板，你决定！**
