# Solacore API 文档索引

## 入口

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## 架构说明

本 API 采用模块化路由架构，主要路由组已拆分为独立子模块：

- **Auth 路由** (`app/routers/auth/`) - 10 个子模块处理认证、OAuth、会话管理
- **Sessions 路由** (`app/routers/sessions/`) - 6 个子模块处理 Solve 会话的创建、列表、流式消息、更新、删除
- **Learn 路由** (`app/routers/learn/`) - 5 个子模块处理学习会话（费曼学习法、分块学习等）
- **Startup 模块** (`app/startup/`) - 6 个模块管理应用初始化、中间件、路由注册

这种架构带来以下优势：
- 易于维护（每个文件 50-200 行，专注单一职责）
- 减少合并冲突（多人协作时不同开发者修改不同模块）
- 便于测试（独立的工具函数可单独测试）
- 代码复用（共享工具减少重复代码 50+ 行）

详见 `docs/ARCHITECTURE.md` 的模块化架构部分。

## 基础信息

- Base URL（本地开发）: `http://localhost:8000`
- Base URL（生产环境）: 以部署域名为准（例如 `https://api.solacore.app`）
- API 版本: `settings.app_version`（默认 `0.1.0`）
- 数据格式: `application/json`；流式接口使用 `text/event-stream` (SSE)

## 认证方式

- Bearer Token: `Authorization: Bearer <access_token>`
- Cookie: `access_token` + `refresh_token` (httpOnly)
- CSRF: 使用 Cookie 进行写操作时需传 `X-CSRF-Token`（可通过 `GET /auth/csrf` 获取）

## 常见错误响应

- 401: `INVALID_TOKEN`
- 403: `FORBIDDEN` / `CSRF_TOKEN_MISSING`
- 404: `NOT_FOUND`
- 500: `INTERNAL_SERVER_ERROR`

标准错误结构示例：

```json
{
  "error": "INVALID_TOKEN",
  "detail": "Token is missing or invalid"
}
```

## 端点索引

### Auth

- `GET /auth/csrf` - 获取 CSRF Token
- `POST /auth/register` - 注册
- `POST /auth/login` - 登录
- `POST /auth/beta-login` - Beta 自动登录
- `POST /auth/refresh` - 刷新 access token
- `POST /auth/forgot-password` - 发送重置邮件
- `POST /auth/reset-password` - 重置密码
- `POST /auth/logout` - 登出
- `POST /auth/oauth/google` - Google OAuth 登录
- `POST /auth/oauth/google/code` - Google OAuth 授权码登录
- `POST /auth/oauth/apple` - Apple Sign-in 登录
- `GET /auth/me` - 获取当前用户
- `GET /auth/devices` - 活跃设备列表
- `DELETE /auth/devices/{device_id}` - 解绑设备
- `GET /auth/sessions` - 活跃会话列表
- `DELETE /auth/sessions/{session_id}` - 终止会话
- `GET /auth/config/features` - 功能开关

### Sessions

- `POST /sessions` - 创建 Solve 会话
- `GET /sessions` - 获取会话列表
- `GET /sessions/{session_id}` - 获取会话详情
- `PATCH /sessions/{session_id}` - 更新会话
- `POST /sessions/{session_id}/messages` - SSE 流式消息

### Subscriptions

- `POST /subscriptions/checkout` - 创建订阅结账会话
- `GET /subscriptions/portal` - 获取订阅管理入口
- `GET /subscriptions/current` - 获取当前订阅状态
- `GET /subscriptions/usage` - 获取订阅使用量

### Account

- `GET /account/export` - 导出账户数据
- `DELETE /account` - 删除账户

### Health

- `GET /health` - 服务健康检查
- `GET /health/ready` - Readiness 探针
- `GET /health/live` - Liveness 探针
