# Prompt Templates API 设计

## 1. 获取模板列表

```http
GET /api/v1/templates
```

**Query 参数**:
- `category`: 可选，筛选分类（learning, life, work, entertainment）
- `limit`: 可选，默认 20
- `popular`: 可选，按使用次数排序

**响应示例**:
```json
{
  "templates": [
    {
      "id": "uuid",
      "role_name": "English Teacher",
      "role_name_cn": "英语老师",
      "category": "learning",
      "description": "帮你练习英语口语，纠正语法错误",
      "icon_emoji": "🎓",
      "usage_count": 1523,
      "welcome_message": "Hello! I'm your English teacher..."
    }
  ],
  "total": 20
}
```

---

## 2. 获取单个模板详情

```http
GET /api/v1/templates/{template_id}
```

**响应示例**:
```json
{
  "id": "uuid",
  "role_name": "Life Coach",
  "role_name_cn": "生活教练",
  "category": "life",
  "system_prompt": "I want you to act as a life coach...",
  "welcome_message": "你好！我是你的生活教练...",
  "description": "帮助你设定目标、制定计划...",
  "icon_emoji": "❤️",
  "usage_count": 856
}
```

---

## 3. 使用模板创建会话（核心功能）

```http
POST /api/v1/sessions
```

**请求 Body**:
```json
{
  "title": "跟英语老师练习口语",
  "template_id": "uuid",           // 新增：模板 ID
  "custom_instructions": "我想练习商务英语"  // 可选：用户补充
}
```

**后端逻辑**:
```python
async def create_session_with_template(
    request: SessionCreateRequest,
    current_user: User,
    db: AsyncSession
):
    # 1. 获取模板
    template = await db.get(PromptTemplate, request.template_id)

    # 2. 创建会话
    session = Session(
        user_id=current_user.id,
        title=request.title,
        template_id=template.id
    )

    # 3. 插入系统消息（提示词）
    system_message = Message(
        session_id=session.id,
        role="system",
        content=template.system_prompt
    )

    # 4. 可选：插入欢迎消息
    if template.welcome_message:
        welcome_msg = Message(
            session_id=session.id,
            role="assistant",
            content=template.welcome_message
        )

    # 5. 更新使用次数
    template.usage_count += 1

    return session
```

**响应示例**:
```json
{
  "id": "session-uuid",
  "title": "跟英语老师练习口语",
  "template_id": "template-uuid",
  "messages": [
    {
      "role": "system",
      "content": "I want you to act as a spoken English teacher..."
    },
    {
      "role": "assistant",
      "content": "Hello! I'm your English teacher. What would you like to talk about?"
    }
  ]
}
```

---

## 4. 管理员：创建/更新模板

```http
POST /api/v1/admin/templates
PUT /api/v1/admin/templates/{template_id}
```

**权限**: 仅管理员

---

## 5. 统计热门模板

```http
GET /api/v1/templates/popular
```

**响应**:
```json
{
  "popular_templates": [
    {"role_name": "English Teacher", "usage_count": 1523},
    {"role_name": "Life Coach", "usage_count": 856}
  ]
}
```

---

## 前端 UI 建议

### 创建会话页面新增"选择角色"入口

```
┌─────────────────────────────────────┐
│  创建新会话                          │
├─────────────────────────────────────┤
│                                     │
│  [空白会话]  [选择 AI 角色 →]        │
│                                     │
│  ┌──────────┬──────────┬──────────┐ │
│  │ 🎓       │ ❤️       │ 💼       │ │
│  │ 英语老师  │ 生活教练  │ 职业顾问 │ │
│  │ 练习口语  │ 规划目标  │ 职业建议 │ │
│  └──────────┴──────────┴──────────┘ │
│                                     │
│  ┌──────────┬──────────┬──────────┐ │
│  │ 🤗       │ ✈️       │ 🍳       │ │
│  │ 倾听朋友  │ 旅行向导  │ 私人厨师 │ │
│  └──────────┴──────────┴──────────┘ │
│                                     │
│  [查看全部 20+ 角色]                │
└─────────────────────────────────────┘
```

---

## 数据迁移脚本

见 `alembic/versions/xxx_add_prompt_templates.py`

---

## 完整提示词数据导入

见 `scripts/import_prompts_from_csv.py` - 从 awesome-chatgpt-prompts 批量导入
