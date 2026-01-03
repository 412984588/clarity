# 学习功能测试指南

**部署状态**: ✅ 已上线 (2026-01-01)
**生产环境**: https://api.solacore.app
**数据库状态**: ✅ 表已创建，迁移已完成

---

## 功能验证结果

### ✅ 已验证的功能

1. **学习工具列表 API**
   - **端点**: `GET https://api.solacore.app/learn/tools`
   - **测试结果**: ✅ 成功返回 10 个学习方法论
   ```json
   {
     "tools": [
       {"id": "pareto", "name": "80/20原则", "estimated_minutes": 5},
       {"id": "feynman", "name": "费曼学习法", "estimated_minutes": 8},
       {"id": "chunking", "name": "分块学习法", "estimated_minutes": 10},
       {"id": "dual_coding", "name": "双编码理论", "estimated_minutes": 8},
       {"id": "interleaving", "name": "主题交叉法", "estimated_minutes": 10},
       {"id": "retrieval", "name": "检索练习", "estimated_minutes": 6},
       {"id": "spaced", "name": "艾宾浩斯复习", "estimated_minutes": 4},
       {"id": "grow", "name": "GROW模型", "estimated_minutes": 10},
       {"id": "socratic", "name": "苏格拉底提问", "estimated_minutes": 10},
       {"id": "error_driven", "name": "错误驱动学习", "estimated_minutes": 8}
     ]
   }
   ```

2. **学习会话列表 API**
   - **端点**: `GET https://api.solacore.app/learn`
   - **测试结果**: ✅ 成功返回会话列表（新账号为空）
   ```json
   {
     "sessions": [],
     "total": 0,
     "limit": 20,
     "offset": 0
   }
   ```

3. **数据库表结构**
   - **learn_sessions**: ✅ 包含所有字段（learning_mode, current_tool, tool_plan）
   - **learn_messages**: ✅ 包含 tool 字段
   - **索引**: ✅ 性能优化索引已创建
   - **外键**: ✅ 关联关系正确

---

## 需要前端配合的测试

以下功能需要从前端页面测试（因为涉及 CSRF token）：

### 1. 创建学习会话
```http
POST https://api.solacore.app/learn
Headers:
  X-CSRF-Token: [从 /auth/csrf 获取]
  Cookie: access_token=...
Body: (可选)
{
  "mode": "quick"  // 或 "deep"
}
```

**预期响应**:
```json
{
  "session_id": "uuid",
  "status": "active",
  "current_step": "start",
  "created_at": "2026-01-01T..."
}
```

### 2. 发送学习消息
```http
POST https://api.solacore.app/learn/{session_id}/messages
Headers:
  X-CSRF-Token: [token]
  Cookie: access_token=...
Body:
{
  "content": "我想学习 Python 编程",
  "step": "start",
  "tool": "feynman"  // 可选
}
```

### 3. 选择学习路径
```http
POST https://api.solacore.app/learn/{session_id}/path
Headers:
  X-CSRF-Token: [token]
Body:
{
  "tool_ids": ["pareto", "feynman", "chunking"]
}
```

### 4. 切换学习工具
```http
PATCH https://api.solacore.app/learn/{session_id}/current-tool
Headers:
  X-CSRF-Token: [token]
Body:
{
  "tool_id": "dual_coding"
}
```

### 5. 查看学习进度
```http
GET https://api.solacore.app/learn/{session_id}/progress
Headers:
  Cookie: access_token=...
```

**预期响应**:
```json
{
  "session_id": "uuid",
  "total_tools": 3,
  "completed_tools": 1,
  "current_tool": "feynman",
  "remaining_tools": ["chunking"],
  "progress_percentage": 33.33
}
```

---

## 快速测试步骤（前端开发者使用）

### 准备工作
1. 访问 https://solacore.app/register 注册测试账号
2. 登录后打开浏览器开发者工具（F12）

### 测试脚本（在浏览器控制台运行）

```javascript
// 1. 获取 CSRF Token
const csrfResp = await fetch('https://api.solacore.app/auth/csrf', {
  credentials: 'include'
});
const { csrf_token } = await csrfResp.json();
console.log('CSRF Token:', csrf_token);

// 2. 获取学习工具列表
const toolsResp = await fetch('https://api.solacore.app/learn/tools', {
  credentials: 'include'
});
const { tools } = await toolsResp.json();
console.log('可用工具:', tools.map(t => t.name));

// 3. 创建学习会话
const createResp = await fetch('https://api.solacore.app/learn', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token
  },
  credentials: 'include'
});
const session = await createResp.json();
console.log('会话已创建:', session);

// 4. 发送第一条消息
const msgResp = await fetch(`https://api.solacore.app/learn/${session.session_id}/messages`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token
  },
  credentials: 'include',
  body: JSON.stringify({
    content: '我想学习 React Hooks',
    step: 'start'
  })
});
const message = await msgResp.json();
console.log('AI 回复:', message);

// 5. 查看会话历史
const historyResp = await fetch(`https://api.solacore.app/learn/${session.session_id}/messages`, {
  credentials: 'include'
});
const { messages } = await historyResp.json();
console.log('对话历史:', messages);
```

---

## 已知限制

1. **CSRF Token 跨域限制**
   - 从本地终端 curl 测试会失败（CSRF_TOKEN_INVALID）
   - 必须从浏览器/前端页面测试（同域名）
   - Cookie 的 domain 设置为 `.solacore.app`

2. **SSL 证书警告**
   - 当前使用自签名证书
   - 浏览器会显示"不安全"警告（可忽略，不影响功能）
   - 后续需要配置 Let's Encrypt 正式证书

---

## 后端 API 端点完整列表

| 方法 | 端点 | 功能 | 认证 | CSRF |
|------|------|------|------|------|
| GET | `/learn/tools` | 获取学习工具列表 | ✅ | ❌ |
| GET | `/learn` | 获取会话列表 | ✅ | ❌ |
| POST | `/learn` | 创建学习会话 | ✅ | ✅ |
| GET | `/learn/{id}/messages` | 获取消息历史 | ✅ | ❌ |
| POST | `/learn/{id}/messages` | 发送消息 | ✅ | ✅ |
| POST | `/learn/{id}/path` | 选择学习路径 | ✅ | ✅ |
| PATCH | `/learn/{id}/current-tool` | 切换工具 | ✅ | ✅ |
| GET | `/learn/{id}/progress` | 查看进度 | ✅ | ❌ |
| PATCH | `/learn/{id}` | 更新会话状态 | ✅ | ✅ |
| DELETE | `/learn/{id}` | 删除会话 | ✅ | ✅ |

---

## 数据库验证命令

```bash
# SSH 登录到服务器
ssh linuxuser@139.180.223.98

# 查看学习相关的表
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres solacore -c "
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    AND table_name LIKE 'learn%'
    ORDER BY table_name;"

# 查看表结构
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres solacore -c "\d learn_sessions"

# 查看现有会话（如果有）
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres solacore -c "SELECT id, user_id, status, current_step, learning_mode FROM learn_sessions LIMIT 10;"
```

---

## 故障排查

### 问题 1: CSRF Token 无效
**现象**: `{"error": "CSRF_TOKEN_INVALID"}`
**原因**: 跨域或 token 过期
**解决**: 从浏览器控制台重新获取 token

### 问题 2: 401 Unauthorized
**现象**: `{"error": "INVALID_TOKEN"}`
**原因**: 未登录或 token 过期
**解决**: 重新登录

### 问题 3: 数据库连接失败
**现象**: `{"status": "degraded", "checks": {"database": "error"}}`
**原因**: PostgreSQL 密码认证失败
**解决**: 运行修复脚本
```bash
cd /home/linuxuser/solacore/solacore-api
bash scripts/fix-prod-db.sh
```

---

**最后更新**: 2026-01-01
**维护者**: Claude + 老板
