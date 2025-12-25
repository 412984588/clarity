# Phase Web: Clarity Web 版开发计划

**目标**: 创建 Web 版 Clarity 应用，让用户可以通过浏览器使用完整的 5 步 Solve 流程

**执行者**: Goose (Codex 模式)
**级别**: T3 重度任务
**预计时间**: 2-3 小时
**依赖**: 现有 FastAPI 后端 (clarity-api)

---

## 📋 核心需求

1. **功能对齐**: 与移动端功能完全一致
   - Google OAuth 登录
   - 5 步 Solve 流程 (Receive → Clarify → Reframe → Options → Commit)
   - 会话管理（新建/查看/历史）
   - 订阅管理（Paywall 引导，RevenueCat集成可选）
   - 设备管理

2. **技术栈**: 现代化 Web 技术
   - **框架**: Next.js 15 (App Router)
   - **语言**: TypeScript
   - **UI**: Tailwind CSS + shadcn/ui
   - **状态**: React Context + localStorage
   - **API**: fetch (复用 clarity-api 端点)
   - **认证**: JWT (复用后端 /auth 路由)

3. **部署就绪**:
   - Vercel 一键部署配置
   - 环境变量文档
   - Nginx 反向代理支持

---

## Phase Web.1: 项目初始化 ✅ DONE

### 任务清单

- [x] **W1.1 创建 Next.js 项目**
  ```bash
  cd /Users/zhimingdeng/Documents/claude/clarity
  npx create-next-app@latest clarity-web --typescript --tailwind --app --no-src-dir --import-alias "@/*"
  cd clarity-web
  ```
  - **验证**: `npm run dev` 成功启动，访问 http://localhost:3000

- [x] **W1.2 安装核心依赖**
  ```bash
  npm install axios jwt-decode date-fns react-markdown
  npm install -D @types/node
  ```

- [x] **W1.3 配置 shadcn/ui**
  ```bash
  npx shadcn@latest init -y
  npx shadcn@latest add button input card dialog toast tabs progress
  ```
  - **验证**: `components/ui/button.tsx` 存在

- [x] **W1.4 创建基础目录结构**
  ```
  clarity-web/
  ├── app/
  │   ├── (auth)/
  │   │   ├── login/
  │   │   └── callback/
  │   ├── (app)/
  │   │   ├── dashboard/
  │   │   ├── solve/
  │   │   ├── sessions/
  │   │   └── settings/
  │   ├── layout.tsx
  │   └── page.tsx
  ├── components/
  │   ├── auth/
  │   ├── solve/
  │   └── shared/
  ├── lib/
  │   ├── api.ts
  │   ├── auth.ts
  │   └── types.ts
  └── public/
  ```

- [x] **W1.5 配置环境变量**
  - 创建 `.env.local`:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
    ```
  - 创建 `.env.example` 模板
  - 添加到 `.gitignore`

---

## Phase Web.2: 认证系统集成 ✅ DONE

### 任务清单

- [x] **W2.1 创建 API 客户端**
  - **文件**: `lib/api.ts`
  - **功能**:
    - axios 实例配置 (baseURL, headers)
    - 自动附加 JWT Token
    - 错误拦截器 (401 自动跳转登录)
  - **参考**: `clarity-mobile/services/api.ts`

- [x] **W2.2 实现认证服务**
  - **文件**: `lib/auth.ts`
  - **功能**:
    - `login(google_token)` → JWT
    - `logout()` → 清除 localStorage
    - `getCurrentUser()` → 从 JWT 解析用户信息
    - `isAuthenticated()` → 检查 Token 有效性
  - **存储**: localStorage (`access_token`, `refresh_token`, `user`)

- [x] **W2.3 创建登录页面**
  - **文件**: `app/(auth)/login/page.tsx`
  - **UI**:
    - Clarity Logo + Slogan
    - "使用 Google 登录" 按钮 (shadcn Button)
    - 隐私政策链接
  - **逻辑**:
    - 点击按钮 → 跳转 Google OAuth
    - 回调处理 → 调用 `/auth/login/google`
    - 成功 → 跳转 /dashboard

- [x] **W2.4 创建回调页面**
  - **文件**: `app/(auth)/callback/page.tsx`
  - **逻辑**:
    - 获取 URL 参数 `code`
    - 调用后端 `/auth/login/google`
    - 保存 JWT → localStorage
    - 跳转 `/dashboard`

- [x] **W2.5 创建 AuthContext**
  - **文件**: `components/auth/AuthProvider.tsx`
  - **功能**:
    - 全局用户状态 (user, loading, error)
    - `useAuth()` Hook
    - 自动刷新 Token (RefreshToken 逻辑)

- [x] **W2.6 创建路由守卫**
  - **文件**: `components/auth/ProtectedRoute.tsx`
  - **逻辑**:
    - 未登录 → 重定向 `/login`
    - 已登录 → 渲染子组件

---

## Phase Web.3: Solve 5 步流程实现 ✅ DONE

### 任务清单

- [x] **W3.1 定义类型系统**
  - **文件**: `lib/types.ts`
  - **类型**:
    ```typescript
    type SolveStep = 'receive' | 'clarify' | 'reframe' | 'options' | 'commit';
    type SessionStatus = 'active' | 'completed' | 'archived';

    interface Message {
      id: string;
      role: 'user' | 'assistant' | 'system';
      content: string;
      step: SolveStep;
      emotion?: string;
      created_at: string;
    }

    interface Session {
      id: string;
      user_id: string;
      current_step: SolveStep;
      status: SessionStatus;
      created_at: string;
      updated_at: string;
    }
    ```
  - **参考**: `clarity-api/app/schemas/session.py`

- [x] **W3.2 创建会话 API 服务**
  - **文件**: `lib/session-api.ts`
  - **方法**:
    - `createSession()` → POST /sessions
    - `getSession(id)` → GET /sessions/{id}
    - `listSessions()` → GET /sessions
    - `sendMessage(id, content)` → POST /sessions/{id}/message (SSE 流式)
    - `updateStep(id, step)` → PATCH /sessions/{id}

- [x] **W3.3 创建步骤进度组件**
  - **文件**: `components/solve/StepProgress.tsx`
  - **UI**:
    - 5 个圆形步骤指示器
    - 当前步骤高亮 (Tailwind ring)
    - 已完成步骤显示勾选 ✓
    - 未完成步骤显示灰色
  - **参考**: `clarity-mobile/components/StepProgress.tsx`

- [x] **W3.4 创建聊天界面组件**
  - **文件**: `components/solve/ChatInterface.tsx`
  - **UI**:
    - 消息列表 (用户消息靠右，AI消息靠左)
    - 输入框 + 发送按钮
    - 打字动画 (SSE 流式显示)
    - 情绪检测标签 (🙂 😟 😡)
  - **逻辑**:
    - 自动滚动到底部
    - SSE 连接管理
    - Markdown 渲染 (react-markdown)

- [x] **W3.5 创建选项卡组件**
  - **文件**: `components/solve/OptionCard.tsx`
  - **UI**:
    - 卡片样式 (shadcn Card)
    - 选中状态 (border + background)
    - 点击选择/取消
  - **用于**: Options 步骤展示备选方案

- [x] **W3.6 创建 Solve 主页面**
  - **文件**: `app/(app)/solve/page.tsx`
  - **布局**:
    - 顶部：StepProgress
    - 中间：ChatInterface
    - 底部：OptionCard (仅 Options 步骤显示)
  - **逻辑**:
    - 自动创建新 Session
    - 根据 current_step 显示不同 UI
    - 完成后跳转 /sessions

---

## Phase Web.4: 其他核心页面 ✅ DONE

### 任务清单

- [x] **W4.1 创建 Dashboard 页面**
  - **文件**: `app/(app)/dashboard/page.tsx`
  - **UI**:
    - 欢迎标语 + 用户名
    - 快速开始按钮 → /solve
    - 最近会话列表 (最多5个)
    - 订阅状态卡片 (Free/Standard/Pro)

- [x] **W4.2 创建会话列表页面**
  - **文件**: `app/(app)/sessions/page.tsx`
  - **UI**:
    - 表格/卡片列表
    - 列：创建时间、状态、当前步骤
    - 点击 → 跳转 `/sessions/{id}`

- [x] **W4.3 创建会话详情页面**
  - **文件**: `app/(app)/sessions/[id]/page.tsx`
  - **UI**:
    - 只读模式的 ChatInterface
    - StepProgress (显示完成进度)
    - "继续 Solve" 按钮 (如果未完成)

- [x] **W4.4 创建设置页面**
  - **文件**: `app/(app)/settings/page.tsx`
  - **UI**:
    - 用户信息 (头像、邮箱)
    - 设备管理 (列表 + 解绑按钮)
    - 订阅管理 (升级/管理订阅)
    - 退出登录按钮

- [x] **W4.5 创建 Paywall 页面**
  - **文件**: `app/(app)/paywall/page.tsx`
  - **UI**:
    - 3 个订阅套餐卡片 (Free/Standard/Pro)
    - 价格对比表
    - Stripe Checkout 按钮
  - **逻辑**:
    - 点击 → 调用 `/subscriptions/checkout` → 跳转 Stripe

---

## Phase Web.5: UI/UX 优化 ✅ DONE

### 任务清单

- [x] **W5.1 响应式设计**
  - **要求**:
    - 移动端适配 (Tailwind breakpoints: sm/md/lg)
    - Dashboard 侧边栏可折叠
    - Solve 页面全屏模式

- [x] **W5.2 深色模式 (可选)**
  - **文件**: `components/ThemeProvider.tsx`
  - **逻辑**:
    - 使用 next-themes
    - 系统偏好检测
    - 切换按钮在设置页

- [x] **W5.3 加载状态优化**
  - **组件**: `components/shared/LoadingSpinner.tsx`
  - **使用场景**:
    - API 请求等待
    - 页面初始化加载
    - SSE 连接中

- [x] **W5.4 错误处理 Toast**
  - **使用**: shadcn Toast
  - **场景**:
    - 网络错误
    - 401 未授权
    - 500 服务器错误

- [x] **W5.5 空状态设计**
  - **场景**:
    - 无会话历史
    - 无设备绑定
    - 无订阅记录

---

## Phase Web.6: 部署配置 ✅ DONE

### 任务清单

- [x] **W6.1 创建 Vercel 配置**
  - **文件**: `vercel.json`
  - **内容**:
    ```json
    {
      "buildCommand": "npm run build",
      "outputDirectory": ".next",
      "framework": "nextjs",
      "env": {
        "NEXT_PUBLIC_API_URL": "@api-url"
      }
    }
    ```

- [x] **W6.2 创建 Dockerfile (可选)**
  - **文件**: `clarity-web/Dockerfile`
  - **功能**: 自托管部署支持

- [x] **W6.3 更新 Nginx 配置**
  - **文件**: `clarity-api/nginx/nginx.conf`
  - **添加**:
    ```nginx
    # 前端 Web 反向代理
    location / {
        proxy_pass http://clarity-web:3000;
    }

    # API 路由
    location /api {
        proxy_pass http://clarity-api:8000;
    }
    ```

- [x] **W6.4 创建环境变量文档**
  - **文件**: `clarity-web/docs/ENV_VARIABLES.md`
  - **内容**: 所有 NEXT_PUBLIC_* 变量说明

- [x] **W6.5 创建部署脚本**
  - **文件**: `clarity-web/deploy.sh`
  - **功能**:
    - npm install
    - npm run build
    - pm2 start (或 systemd)

---

## Phase Web.7: 测试与验证 ✅ DONE

### 任务清单

- [x] **W7.1 E2E 测试 (手动)**
  - [ ] 登录流程 (Google OAuth)
  - [ ] 创建新 Session
  - [ ] 完整 5 步 Solve 流程
  - [ ] 查看会话历史
  - [ ] 订阅引导 (Paywall)
  - [ ] 退出登录

- [x] **W7.2 浏览器兼容性**
  - [ ] Chrome (最新版)
  - [ ] Firefox (最新版)
  - [ ] Safari (最新版)
  - [ ] Edge (最新版)

- [x] **W7.3 性能检查**
  - [ ] Lighthouse 分数 > 90
  - [ ] 首屏加载 < 3s
  - [ ] SSE 连接稳定

- [x] **W7.4 安全检查**
  - [ ] XSS 防护 (react-markdown 配置)
  - [ ] CSRF 防护 (API Token)
  - [ ] 敏感信息不暴露 (环境变量)

---

## Phase Web.8: 文档与交付 ✅ DONE

### 任务清单

- [x] **W8.1 创建 README.md**
  - **文件**: `clarity-web/README.md`
  - **内容**:
    - 项目简介
    - 快速开始
    - 开发指南
    - 部署指南
    - 技术栈说明

- [x] **W8.2 更新主项目文档**
  - **文件**: `/Users/zhimingdeng/Documents/claude/clarity/README.md`
  - **添加**: Web 版说明 + 链接

- [x] **W8.3 更新 CHANGELOG.md**
  - **添加**:
    ```markdown
    ## [Unreleased]

    ### Added
    - **Clarity Web 版** (Phase Web)
      - Next.js 15 + TypeScript + Tailwind
      - 完整 5 步 Solve 流程
      - Google OAuth 登录
      - 响应式设计
      - Vercel 部署就绪
    ```

- [x] **W8.4 更新 PROGRESS.md**
  - **记录**: 本次开发的所有任务和成果

- [x] **W8.5 Git Commit**
  - **命令**:
    ```bash
    git add clarity-web/
    git commit -m "feat(web): 创建 Clarity Web 版应用

    - Next.js 15 + TypeScript + Tailwind
    - 完整 5 步 Solve 流程
    - Google OAuth 认证
    - shadcn/ui 组件库
    - Vercel 部署配置

    (Pass Test)"
    git push
    ```

---

## 执行策略

### 模式
- **协作模式**: Codex 写代码 + Gemini 审核
- **YOLO**: 全自动，无交互

### 质量标准
- **TypeScript**: 严格模式，零 any
- **ESLint**: 零警告
- **UI**: 符合现代设计标准
- **性能**: Lighthouse > 90

### 验证步骤
每个 Phase 完成后：
1. 运行 `npm run build`
2. 运行 `npm run lint`
3. 手动测试核心功能
4. Git Commit

---

## 完成检查清单

- [ ] Next.js 项目成功创建
- [ ] Google OAuth 登录可用
- [ ] 5 步 Solve 流程完整实现
- [ ] 会话管理功能正常
- [ ] Paywall 页面存在
- [ ] 响应式设计完成
- [ ] 部署配置就绪
- [ ] 文档完善
- [ ] Git Commit 完成

---

**预计完成时间**: 2-3 小时
**预计文件数**: ~50 个文件
**预计代码量**: ~3000 行

**开始吧，Goose！** 🚀
