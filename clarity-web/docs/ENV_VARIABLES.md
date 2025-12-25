# 环境变量说明

所有 `NEXT_PUBLIC_*` 变量会在构建时注入到前端，请避免放敏感信息。

## 变量列表

| 变量 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | 是 | 后端 API 地址，供前端请求使用。 | `http://localhost:8000` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | 是 | Google OAuth Client ID，用于登录授权。 | `1234567890-xxxxx.apps.googleusercontent.com` |
| `NEXT_PUBLIC_SENTRY_DSN` | 否 | Sentry DSN，用于前端错误上报。 | `https://examplePublicKey@o0.ingest.sentry.io/0` |

## 本地开发

1. 复制模板：`cp .env.example .env.local`
2. 按需填写变量值后启动：`npm run dev`
