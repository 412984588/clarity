# App Store / Play Store Submission Checklist

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose

本文档是 Clarity 应用提交至 Apple App Store 和 Google Play Store 的完整检查清单。确保所有必要资产、配置和合规要求在提交前已满足。

---

## iOS Submission Checklist

### Account & Certificates

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Apple Developer Program 已注册 ($99/年) | [ ] | **BLOCKER** |
| 2 | App Store Connect 账号已创建 | [ ] | |
| 3 | Distribution Certificate 已生成 | [ ] | |
| 4 | Provisioning Profile (Distribution) 已创建 | [ ] | |
| 5 | Push Notification Certificate 已配置 | [ ] | 如使用推送 |

### App Configuration

| # | Item | Status | Notes |
|---|------|--------|-------|
| 6 | Bundle ID 已在 App Store Connect 注册 | [ ] | `com.clarity.app` |
| 7 | App Name 已确认（无冲突） | [ ] | "Clarity" |
| 8 | Primary Category 已选择 | [ ] | Health & Fitness / Lifestyle |
| 9 | Secondary Category 已选择（可选） | [ ] | |
| 10 | Age Rating 问卷已完成 | [ ] | |
| 11 | App Privacy 问卷已完成 | [ ] | 数据收集声明 |

### Build & Submission

| # | Item | Status | Notes |
|---|------|--------|-------|
| 12 | EAS Build (Production) 已成功 | [ ] | |
| 13 | Build 已上传至 App Store Connect | [ ] | |
| 14 | 版本号符合规范 (CFBundleShortVersionString) | [ ] | 1.0.0 |
| 15 | Build 号递增 (CFBundleVersion) | [ ] | |

### Review Preparation

| # | Item | Status | Notes |
|---|------|--------|-------|
| 16 | 截图已上传（所有设备尺寸） | [ ] | 见 Required Assets |
| 17 | App 描述已填写（中/英） | [ ] | |
| 18 | Keywords 已填写 | [ ] | |
| 19 | Support URL 已填写 | [ ] | |
| 20 | Privacy Policy URL 已填写 | [ ] | **必须** |
| 21 | Review Notes 已填写 | [ ] | 测试账号、特殊说明 |
| 22 | In-App Purchase 已配置（如有） | [ ] | 订阅产品 |
| 23 | Sign in with Apple 已实现（如用第三方登录） | [ ] | Apple 要求 |
| 24 | In-app Account Deletion 已提供 | [ ] | App Store 要求 |

---

## Android Submission Checklist

### Account & Setup

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Google Play Developer 账号已注册 ($25 一次性) | [ ] | **BLOCKER** |
| 2 | Google Play Console 已访问 | [ ] | |
| 3 | Merchant Account 已设置（如有付费功能） | [ ] | |

### App Configuration

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4 | Package Name 已确认 | [ ] | `com.clarity.app` |
| 5 | App Name 已填写 | [ ] | "Clarity" |
| 6 | App Category 已选择 | [ ] | Health & Fitness |
| 7 | Content Rating 问卷已完成 | [ ] | IARC |
| 8 | Data Safety 问卷已完成 | [ ] | 数据收集声明 |
| 9 | Target Audience 已声明 | [ ] | 不面向儿童 |

### Build & Submission

| # | Item | Status | Notes |
|---|------|--------|-------|
| 10 | EAS Build (Production) 已成功 | [ ] | AAB 格式 |
| 11 | AAB 已上传至 Play Console | [ ] | |
| 12 | Version Code 递增 | [ ] | |
| 13 | Version Name 符合规范 | [ ] | 1.0.0 |
| 14 | Signing Key 已配置 | [ ] | Play App Signing |

### Store Listing

| # | Item | Status | Notes |
|---|------|--------|-------|
| 15 | 截图已上传（手机 + 平板） | [ ] | 见 Required Assets |
| 16 | Feature Graphic 已上传 | [ ] | 1024x500 |
| 17 | App 描述已填写（中/英） | [ ] | 短描述 + 完整描述 |
| 18 | 联系邮箱已填写 | [ ] | |
| 19 | Privacy Policy URL 已填写 | [ ] | **必须** |
| 20 | In-App Products 已配置（如有） | [ ] | 订阅产品 |

### Compliance

| # | Item | Status | Notes |
|---|------|--------|-------|
| 21 | App Access 说明已填写 | [ ] | 如需登录才能使用 |
| 22 | Ads Declaration 已完成 | [ ] | 是否包含广告 |
| 23 | Government Apps Declaration（如适用） | [ ] | |
| 24 | In-app Account Deletion 已提供 | [ ] | Play Store 要求 |

---

## Required Assets

### Screenshots

| Platform | Device | Size | Quantity | Status |
|----------|--------|------|----------|--------|
| **iOS** | iPhone 6.7" (14 Pro Max) | 1290 x 2796 | 3-10 | [ ] |
| **iOS** | iPhone 6.5" (11 Pro Max) | 1242 x 2688 | 3-10 | [ ] |
| **iOS** | iPhone 5.5" (8 Plus) | 1242 x 2208 | 3-10 | [ ] |
| **iOS** | iPad Pro 12.9" (可选) | 2048 x 2732 | 3-10 | [ ] |
| **Android** | Phone | 1080 x 1920+ | 2-8 | [ ] |
| **Android** | 7" Tablet (可选) | 1200 x 1920 | 2-8 | [ ] |
| **Android** | 10" Tablet (可选) | 1600 x 2560 | 2-8 | [ ] |

### Graphics

| Asset | Size | Format | Platform | Status |
|-------|------|--------|----------|--------|
| App Icon | 1024 x 1024 | PNG (no alpha) | Both | [ ] |
| Feature Graphic | 1024 x 500 | PNG/JPG | Android | [ ] |
| Promo Video (可选) | 15-30s | MP4/MOV | Both | [ ] |

### Text Content

| Content | Max Length | Languages | Status |
|---------|------------|-----------|--------|
| App Name | 30 chars | EN, ZH | [ ] |
| Subtitle (iOS) | 30 chars | EN, ZH | [ ] |
| Short Description (Android) | 80 chars | EN, ZH | [ ] |
| Full Description | 4000 chars | EN, ZH | [ ] |
| What's New | 4000 chars | EN, ZH | [ ] |
| Keywords (iOS) | 100 chars | EN, ZH | [ ] |
| Promotional Text (iOS, 可选) | 170 chars | EN, ZH | [ ] |

### URLs

| URL | Required | Status |
|-----|----------|--------|
| Privacy Policy | **必须** | [ ] |
| Terms of Service | 推荐 | [ ] |
| Support URL | **必须** | [ ] |
| Marketing URL (可选) | 可选 | [ ] |

---

## Versioning & Release Tracks

### iOS Release Strategy

| Track | Purpose | Audience |
|-------|---------|----------|
| **TestFlight Internal** | 内部测试 | 团队成员 (最多 100 人) |
| **TestFlight External** | 公开测试 | 外部测试者 (最多 10,000 人) |
| **App Store** | 正式发布 | 所有用户 |

### Android Release Strategy

| Track | Purpose | Audience |
|-------|---------|----------|
| **Internal Testing** | 内部测试 | 团队成员 (最多 100 人) |
| **Closed Testing** | 受限测试 | 邀请用户 |
| **Open Testing** | 公开测试 | 任何人可加入 |
| **Production** | 正式发布 | 所有用户 |

### Staged Rollout (Android)

| Stage | Percentage | Duration |
|-------|------------|----------|
| Stage 1 | 5% | 24-48 hours |
| Stage 2 | 20% | 24-48 hours |
| Stage 3 | 50% | 24-48 hours |
| Stage 4 | 100% | - |

---

## Review Notes / Reviewer Instructions

### Demo Account

```
Email: reviewer@clarity.app
Password: [待填写]
```

### Special Instructions

```
[待填写：任何需要告知审核人员的特殊说明]

示例：
- 本应用需要登录才能使用核心功能
- 订阅功能使用沙盒测试账号测试
- 情绪检测功能需要进行完整对话才能触发
```

### Notes for Apple Review

```
[待填写]
```

### Notes for Google Review

```
[待填写]
```

---

## Blockers

| Blocker | Platform | Impact | Status | Resolution |
|---------|----------|--------|--------|------------|
| **Apple Developer Account** | iOS | 无法构建/提交 | BLOCKED | 注册 Apple Developer Program |
| **Google Play Account** | Android | 无法提交 | BLOCKED | 注册 Google Play Developer |
| **Privacy Policy URL** | Both | 必须有有效 URL | PENDING | 部署隐私政策页面（草稿：`docs/release/privacy.md`） |
| **Support URL** | Both | 必须有有效 URL | PENDING | 部署支持页面（草稿：`docs/release/support.md`） |
| **Terms of Service** | Both | 推荐 | PENDING | 部署服务条款页面 |
| **In-App Purchase Setup** | Both | 订阅功能必须 | PENDING | 配置 Stripe/RevenueCat |
| **Sign in with Apple** | iOS | 若用第三方登录则必须 | PENDING | 实现 Apple Sign-In |
| **Payment Compliance** | Both | 订阅必须 | PENDING | 符合各地区法规 |

---

## Submission Timeline

| Phase | iOS | Android | Notes |
|-------|-----|---------|-------|
| **Build Ready** | - | - | EAS Build 成功 |
| **Assets Ready** | - | - | 截图、描述、图标 |
| **Submit for Review** | Day 0 | Day 0 | |
| **Review Period** | 1-7 days | 1-3 days | 首次可能更长 |
| **Approval** | - | - | |
| **Release** | Manual / Auto | Manual / Staged | 可选择立即或定时 |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
| Launch Readiness Scorecard | `docs/release/launch-readiness.md` | 上线准备度评估 |
| Release Checklist | `docs/release/release-checklist.md` | 发布检查清单 |
| Demo Script | `docs/release/demo-script.md` | 演示话术（可用于描述参考） |
| Privacy Policy | `docs/release/privacy.md` | 隐私政策 |
| EAS Preview | `docs/release/eas-preview.md` | EAS 构建配置 |
