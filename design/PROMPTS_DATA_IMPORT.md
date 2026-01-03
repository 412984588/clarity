# 提示词模板数据导入流程

**日期**: 2026-01-01
**数据来源**: [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)
**状态**: ✅ 数据准备完成，等待数据库迁移

---

## 📊 数据概览

| 指标 | 数值 |
|------|------|
| 数据源 CSV 行数 | 20,860 行 |
| 生成的提示词模板数量 | 855 个 |
| 生成的 SQL 文件大小 | 1.4 MB |
| 生成的 SQL 文件行数 | 29,814 行 |
| 推荐优先集成角色数量 | 20 个 |

---

## 📋 执行步骤

### 1. 下载数据源

```bash
cd /Users/zhimingdeng/Documents/claude/clarity/design
curl -o prompts.csv https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv
```

**结果**: 下载成功，20,860 行 CSV 数据

### 2. 运行导入脚本

```bash
python3 import_prompts_script.py prompts.csv
```

**输出**:
```
✅ 已生成 prompts_seed.sql
📊 共 855 个提示词模板

📌 推荐优先集成的 20 个角色：
 1. 📚 English Teacher           (英语老师)
 2. ❤️ Career Counselor          (职业顾问)
 3. 📚 Essay Writer              ()
 4. 📚 Note-taking Assistant     ()
 5. 📚 Etymologist               ()
 6. ❤️ Life Coach                (生活教练)
 7. ❤️ Mental Health Adviser     (心理健康顾问)
 8. ❤️ Friend                    (倾听的朋友)
 9. ❤️ Personal Trainer          (健身教练)
10. ❤️ Dietitian                 (营养师)
11. 💼 Resume                    (简历助手)
12. 💼 Interviewer               (面试官)
13. 💼 Social Media Manager      (社交媒体经理)
14. 💼 Salesperson               (销售顾问)
15. 💼 IT Architect              ()
16. 🎨 Storyteller               (故事大师)
17. 🎨 Travel Guide              (旅行向导)
18. 🎨 Chef                      (私人厨师)
19. 🎨 Interior Decorator        (室内设计师)
20. 📚 Poet                      (诗人)
```

### 3. 生成的文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `prompts.csv` | ~1.1 MB | 原始数据源 |
| `prompts_seed.sql` | 1.4 MB | 生成的 SQL 插入语句 |

---

## 🗄️ 数据库表结构

生成的 SQL 针对以下表结构：

```sql
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) UNIQUE NOT NULL,
    role_name_cn VARCHAR(255),
    category VARCHAR(50) NOT NULL,
    system_prompt TEXT NOT NULL,
    welcome_message TEXT,
    icon_emoji VARCHAR(10),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🏷️ 分类系统

提示词模板被自动分类为 5 个类别：

| 分类 | Emoji | 说明 | 示例角色 |
|------|-------|------|----------|
| **learning** 📚 | 📚 | 学习成长 | English Teacher, Essay Writer, Note-taking Assistant |
| **life** ❤️ | ❤️ | 生活健康 | Life Coach, Mental Health Adviser, Personal Trainer |
| **work** 💼 | 💼 | 工作职场 | Resume, Interviewer, Social Media Manager |
| **entertainment** 🎨 | 🎨 | 娱乐创意 | Storyteller, Travel Guide, Chef, Poet |
| **tech** 💻 | 💻 | 技术开发 | Linux Terminal, JavaScript Console, IT Architect |

---

## 📌 推荐的 20 个优先角色（详细说明）

### 学习成长（5个）

1. **📚 English Teacher (英语老师)**
   - 系统提示: "I want you to act as a spoken English teacher and improver..."
   - 欢迎消息: "Hello! I'm your Spoken English Teacher and Improver. Let's learn together!"
   - 用途: 英语口语练习和纠错

2. **❤️ Career Counselor (职业顾问)**
   - 系统提示: "I want you to act as a career counselor..."
   - 欢迎消息: "你好！我是你的职业顾问。有什么可以帮你的吗？"
   - 用途: 职业规划和发展建议

3. **📚 Essay Writer**
   - 系统提示: "I want you to act as an essay writer..."
   - 欢迎消息: "Hello! I'm your Essay Writer. Let's learn together!"
   - 用途: 论文写作辅导

4. **📚 Note-taking Assistant**
   - 系统提示: "I want you to act as a note-taking assistant..."
   - 欢迎消息: "Hello! I'm your Note-taking Assistant. Let's learn together!"
   - 用途: 笔记整理和总结

5. **📚 Etymologist**
   - 系统提示: "I want you to act as a etymologist..."
   - 欢迎消息: "Hello! I'm your Etymologist. Let's learn together!"
   - 用途: 词源学研究

### 生活健康（5个）

6. **❤️ Life Coach (生活教练)**
   - 系统提示: "I want you to act as a life coach. I will provide some details about my current situation and goals..."
   - 欢迎消息: "你好！我是你的生活教练。有什么可以帮你的吗？"
   - 用途: 生活规划和目标设定

7. **❤️ Mental Health Adviser (心理健康顾问)**
   - 系统提示: "I want you to act as a mental health adviser..."
   - 欢迎消息: "你好！我是你的心理健康顾问。有什么可以帮你的吗？"
   - 用途: 心理健康咨询

8. **❤️ Friend (倾听的朋友)**
   - 系统提示: "I want you to act as my friend..."
   - 欢迎消息: "你好！我是你的倾听的朋友。有什么可以帮你的吗？"
   - 用途: 倾诉和情感支持

9. **❤️ Personal Trainer (健身教练)**
   - 系统提示: "I want you to act as a personal trainer..."
   - 欢迎消息: "你好！我是你的健身教练。有什么可以帮你的吗？"
   - 用途: 健身计划和指导

10. **❤️ Dietitian (营养师)**
    - 系统提示: "I want you to act as a dietitian..."
    - 欢迎消息: "你好！我是你的营养师。有什么可以帮你的吗？"
    - 用途: 营养咨询和饮食建议

### 工作职场（5个）

11. **💼 Resume (简历助手)**
    - 系统提示: "I want you to act as a resume editor..."
    - 欢迎消息: "你好！我是简历助手。准备好开始了吗？"
    - 用途: 简历编写和优化

12. **💼 Interviewer (面试官)**
    - 系统提示: "I want you to act as an interviewer. I will be the candidate..."
    - 欢迎消息: "你好！我是面试官。准备好开始了吗？"
    - 用途: 模拟面试练习

13. **💼 Social Media Manager (社交媒体经理)**
    - 系统提示: "I want you to act as a social media manager..."
    - 欢迎消息: "你好！我是社交媒体经理。准备好开始了吗？"
    - 用途: 社交媒体策略和内容创作

14. **💼 Salesperson (销售顾问)**
    - 系统提示: "I want you to act as a salesperson..."
    - 欢迎消息: "你好！我是销售顾问。准备好开始了吗？"
    - 用途: 销售技巧和话术

15. **💼 IT Architect**
    - 系统提示: "I want you to act as an IT Architect..."
    - 欢迎消息: "你好！我是IT Architect。准备好开始了吗？"
    - 用途: IT 架构设计和咨询

### 娱乐创意（5个）

16. **🎨 Storyteller (故事大师)**
    - 系统提示: "I want you to act as a storyteller..."
    - 欢迎消息: "嗨！我是故事大师。我们开始吧！"
    - 用途: 创意故事创作

17. **🎨 Travel Guide (旅行向导)**
    - 系统提示: "I want you to act as a travel guide. I will write you my location..."
    - 欢迎消息: "嗨！我是旅行向导。我们开始吧！"
    - 用途: 旅行规划和景点推荐

18. **🎨 Chef (私人厨师)**
    - 系统提示: "I want you to act as my personal chef..."
    - 欢迎消息: "嗨！我是私人厨师。我们开始吧！"
    - 用途: 食谱推荐和烹饪指导

19. **🎨 Interior Decorator (室内设计师)**
    - 系统提示: "I want you to act as an interior decorator..."
    - 欢迎消息: "嗨！我是室内设计师。我们开始吧！"
    - 用途: 室内设计建议

20. **📚 Poet (诗人)**
    - 系统提示: "I want you to act as a poet..."
    - 欢迎消息: "Hello! I'm your Poet. Let's learn together!"
    - 用途: 诗歌创作和鉴赏

---

## 🔍 SQL 示例

### 单个模板的 SQL 结构

```sql
INSERT INTO prompt_templates (role_name, role_name_cn, category, system_prompt, welcome_message, icon_emoji, description, is_active)
VALUES (
    'Life Coach',
    '生活教练',
    'life',
    'I want you to act as a life coach. I will provide some details about my current situation and goals, and it will be your job to come up with strategies that can help me make better decisions and reach those objectives. This could involve offering advice on various topics, such as creating plans for achieving success or dealing with difficult emotions. My first request is "I need help developing healthier habits for managing stress."',
    '你好！我是你的生活教练。有什么可以帮你的吗？',
    '❤️',
    'I want you to act as a life coach. I will provide some details about my current situation and goals,...',
    true
) ON CONFLICT (role_name) DO NOTHING;
```

### 特点

- ✅ 使用 `ON CONFLICT (role_name) DO NOTHING` 避免重复插入
- ✅ SQL 字符串转义（单引号 `'` 转换为 `''`）
- ✅ 自动分类和 Emoji 图标
- ✅ 中英文双语支持
- ✅ 欢迎消息本地化

---

## 📝 数据特征

### 中文名称覆盖率

| 分类 | 有中文名称 | 无中文名称 | 覆盖率 |
|------|-----------|-----------|--------|
| learning | 1 | 4 | 20% |
| life | 5 | 0 | 100% |
| work | 4 | 1 | 80% |
| entertainment | 4 | 1 | 80% |
| tech | 0 | 0 | N/A |
| **总计（推荐 20 个）** | **14** | **6** | **70%** |

**建议**: 未来可补充更多中文名称映射

---

## 🚀 下一步行动

### 立即执行

1. ✅ **数据准备完成** - prompts_seed.sql 已生成
2. ⏳ **等待数据库迁移** - Codex 创建 prompt_templates 表
3. ⏳ **导入数据** - 运行 prompts_seed.sql

### 导入命令（迁移完成后）

```bash
# PostgreSQL
psql -h localhost -U postgres -d solacore -f prompts_seed.sql

# 或使用 Python/Alembic（推荐）
# 在迁移脚本中包含数据种子
```

---

## ⚠️ 注意事项

### 数据质量

1. **提示词长度**: 部分提示词较长（最长超过 2000 字符），确保数据库字段类型为 TEXT
2. **特殊字符**: SQL 已正确转义单引号，但需注意其他特殊字符
3. **重复数据**: 使用 `ON CONFLICT (role_name) DO NOTHING` 避免重复

### 分类准确性

- 脚本基于关键词匹配自动分类，可能存在误分类
- 建议在导入后人工审核分类准确性
- 可通过 UPDATE 语句批量修正分类

### 性能考虑

- 855 条数据插入预计耗时 < 5 秒
- 建议在迁移完成后一次性导入，避免多次执行
- 建议在 role_name 字段上创建唯一索引（已在表结构中定义）

---

## 📊 统计分析

### 按分类统计（全部 855 个模板）

```bash
# 执行统计（示例）
grep "category" prompts_seed.sql | cut -d"'" -f4 | sort | uniq -c | sort -rn
```

**预计分布**:
- learning: ~150 个（17.5%）
- life: ~120 个（14%）
- work: ~180 个（21%）
- entertainment: ~300 个（35%）
- tech: ~105 个（12.5%）

---

## 📚 相关文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 原始数据源 | `design/prompts.csv` | 20,860 行 CSV |
| 导入脚本 | `design/import_prompts_script.py` | Python 数据转换脚本 |
| 生成的 SQL | `design/prompts_seed.sql` | 1.4 MB SQL 插入语句 |
| 本文档 | `design/PROMPTS_DATA_IMPORT.md` | 数据导入流程文档 |

---

## ✅ 验证清单

- [x] CSV 数据已下载（20,860 行）
- [x] 导入脚本运行成功
- [x] SQL 文件已生成（1.4 MB, 29,814 行）
- [x] 审查推荐的 20 个模板
- [x] 文档已完成
- [ ] 等待数据库迁移完成
- [ ] 执行数据导入
- [ ] 验证数据完整性
- [ ] 测试前端集成

---

**文档版本**: v1.0
**最后更新**: 2026-01-01
**准备人**: Claude (AI Assistant)
