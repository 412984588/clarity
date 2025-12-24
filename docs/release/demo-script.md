# Clarity Demo Script + Checklist

**Version**: 1.0
**Duration**: 3 minutes

---

## Demo 目标

展示 Clarity 作为一款 AI 驱动的问题解决助手的核心价值：通过 5 步引导式流程（Receive → Clarify → Reframe → Options → Commit），帮助用户将模糊的困扰转化为清晰的行动计划，并通过情绪检测提供个性化的视觉反馈。

---

## 3 分钟演示话术

### 开场（30 秒）

> "大家好，今天我要展示的是 Clarity——一款帮助人们理清思绪、解决问题的 AI 助手。
>
> 它的核心理念是：很多时候我们不是缺少解决方案，而是没有把问题想清楚。Clarity 通过一个 5 步引导流程，帮你把模糊的困扰变成清晰的行动。"

### 技术架构（30 秒）

> "技术上，Clarity 采用 React Native + Expo 构建移动端，FastAPI + PostgreSQL 作为后端，支持 OpenAI 和 Claude 双引擎。
>
> 所有 AI 响应都是实时流式返回的，用户体验非常流畅。我们还内置了情绪检测，会根据对话内容自动调整界面配色。"

### 功能演示（90 秒）

> "让我演示一下核心流程：
>
> **第一步，Receive**——用户输入困扰，比如'工作压力太大，不知道该不该换工作'。
>
> **第二步，Clarify**——AI 会追问关键细节：'具体是哪方面的压力？工作内容、人际关系还是薪资？'
>
> **第三步，Reframe**——帮用户重新定义问题：'所以核心问题是：如何在保持收入的前提下，减少工作带来的焦虑感。'
>
> **第四步，Options**——给出 3-4 个可选方案，用户可以点击卡片查看详情。
>
> **第五步，Commit**——用户选择一个方案，设定具体的第一步行动和提醒时间。
>
> 注意看背景色——它会根据用户情绪自动变化，焦虑时偏暖色，平静时偏冷色。"

### 收尾（30 秒）

> "目前 Android 预览版已可下载测试，iOS 版待 Apple 开发者账号开通后上线。
>
> 后端上线需要配置：域名、托管服务（Vercel/Railway/Fly.io）、PostgreSQL（Neon/Supabase/RDS）、LLM API Key（OpenAI 或 Anthropic）、Stripe/RevenueCat 生产环境。移动端还需要 Apple Developer 账号（iOS）和 Google Play Console（Android）。
>
> 代码和文档都已准备就绪，有问题欢迎提问！"

---

## Demo Checklist

演示前请逐项确认：

### 环境准备

- [ ] Docker 已启动（`docker info` 无报错）
- [ ] PostgreSQL 容器运行中（`docker compose up -d db`）
- [ ] 后端服务启动（`poetry run uvicorn app.main:app --port 8000`）
- [ ] `/health` 返回 `{"status":"healthy","version":"1.0.0","database":"connected"}`

### 演示账号

- [ ] 准备好测试账号（如 `demo@test.com`）
- [ ] 或准备好注册流程演示

### 移动端

- [ ] Expo 服务启动（`npx expo start`）
- [ ] 模拟器/真机已连接
- [ ] 确认 API URL 指向正确后端

### 内容准备

- [ ] 准备 1-2 个演示场景（如"工作压力"、"人际关系"）
- [ ] 熟悉 5 步流程名称（Receive/Clarify/Reframe/Options/Commit）

### 网络

- [ ] 确认网络稳定（AI 响应需要外网）
- [ ] 如无 LLM API Key，准备好说明"这里会显示 AI 响应"

---

## 常见问题与回答

### Q1: 为什么 iOS 版本还没有？

> "iOS 版本需要 Apple Developer Program 账号（$99/年）才能构建和测试。代码已经写好，账号开通后一天内就能发布 TestFlight 版本。"

### Q2: 域名 `api.clarity.app` 配好了吗？

> "域名还未配置。目前演示的是本机部署版本。正式上线需要购买域名并配置 DNS 指向托管服务商（如 Vercel、Railway 或 Fly.io）。"

### Q3: 支付功能能用吗？

> "当前为**免费内测阶段**，支付功能已关闭。Stripe 和 RevenueCat 的集成代码已完成，但延后激活。内测用户无需付费即可使用所有功能。"

### Q4: Google/Apple 登录能用吗？

> "OAuth 登录代码已集成，但需要在 Google Cloud Console 和 Apple Developer 后台配置生产凭证。演示时建议使用邮箱密码登录。"

### Q5: AI 响应用的是什么模型？

> "支持 OpenAI 和 Anthropic 双引擎，模型可通过环境变量配置。演示时需要配置对应的 API Key。"

### Q6: 数据存在哪里？

> "用户数据存储在 PostgreSQL 数据库中。本机演示使用 Docker 容器，生产环境推荐使用 Neon、Supabase 或 AWS RDS。"

### Q7: 情绪检测准确吗？

> "情绪检测基于启发式规则（关键词匹配 + 权重评分），支持中英西三语，尚未进行系统化评测。后续可接入专业情感分析 API 提升精度。"

### Q8: 上线还需要做什么？

> "**当前阶段为免费内测**，仅需基础设施即可开始测试。
>
> **内测必需**：域名、托管服务（Vercel/Railway/Fly.io）、PostgreSQL（Neon/Supabase/RDS）、LLM API Key（OpenAI 或 Anthropic）。
>
> **延后项目**：Stripe Live Mode、RevenueCat 生产配置（支付功能）、Apple Developer 账号（App Store 提交）、Google Play Console（Play Store 提交）。
>
> 内测用户通过 Android 预览版 APK + 本地部署验证核心功能，无需支付和商店提交。"

---

## Related Documents

- 本机演示运行手册: `docs/release/local-demo-runbook.md`
- 项目状态总结: `docs/release/project-status-summary.md`
- 生产部署指南: `docs/PROD_DEPLOY.md`
