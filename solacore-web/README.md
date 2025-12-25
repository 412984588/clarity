# Solacore Web

Solacore Web 是一个结构化思考与行动规划的前端应用，提供登录、会话记录、步骤引导和仪表盘等功能。

## 技术栈

- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4 + Radix UI
- Axios
- Sentry (可选)

## 快速开始

1. 安装依赖：`npm install`
2. 配置环境变量：`cp .env.example .env.local`
3. 启动开发：`npm run dev`
4. 打开 `http://localhost:3000`

环境变量说明见 `docs/ENV_VARIABLES.md`。

## 开发指南

- 本地开发：`npm run dev`
- 构建产物：`npm run build`
- 生产启动：`npm run start`
- 代码检查：`npm run lint`

## 部署指南

### Vercel

- `vercel.json` 已提供基础配置
- 在 Vercel 项目中设置 `NEXT_PUBLIC_*` 环境变量
- 直接部署即可

### Docker

```bash
docker build -t solacore-web .
docker run -p 3000:3000 --env-file .env.local solacore-web
```

### 脚本

```bash
./deploy.sh
./deploy.sh --start
```

## 目录结构

```
app/                # 路由与页面
  (auth)/           # 登录与回调
  (app)/            # 主应用
components/         # 组件
  auth/             # 鉴权相关
  shared/           # 通用组件
  ui/               # UI 基础组件
lib/                # API 与业务逻辑
public/             # 静态资源
docs/               # 文档
```
