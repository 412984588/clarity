# EAS Secrets 配置文档

**Version**: 1.0
**Last Updated**: 2025-12-25
**适用于**: Clarity Mobile (Expo + React Native)

本文档说明如何为 Expo Application Services (EAS) 配置构建所需的 secrets

---

## 核心概念

### EAS Secrets vs 环境变量

| 类型 | 用途 | 存储位置 | 可见性 |
|------|------|----------|--------|
| **EAS Secrets** | 敏感信息（API Keys）| EAS 云端 | 仅构建时可见 |
| **Environment Variables** | 公开配置（API URL）| `eas.json` | 代码仓库可见 |

**重要**:
- EAS Secrets 永远不会出现在代码仓库中
- 它们在构建时被注入到 `.env` 文件中
- 使用前缀 `EXPO_PUBLIC_` 的变量会打包到应用中

---

## 快速开始

### 1. 安装 EAS CLI
```bash
npm install -g eas-cli
eas login
```

### 2. 设置必需的 Secrets
```bash
# RevenueCat API Keys (用于 iOS/Android 订阅)
eas secret:create --scope project --name EXPO_PUBLIC_REVENUECAT_API_KEY_IOS --value "rc_ios_xxx" --type string
eas secret:create --scope project --name EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID --value "rc_android_xxx" --type string

# Google OAuth Client ID (如果需要)
eas secret:create --scope project --name EXPO_PUBLIC_GOOGLE_CLIENT_ID --value "123456789.apps.googleusercontent.com" --type string
```

### 3. 验证 Secrets
```bash
eas secret:list
```

---

## 必需的 Secrets

### Production Build

| Secret 名称 | 必需 | 说明 | 获取方式 |
|------------|------|------|----------|
| `EXPO_PUBLIC_REVENUECAT_API_KEY_IOS` | 是 | RevenueCat iOS 公钥 | [RevenueCat Dashboard](https://app.revenuecat.com) → API Keys |
| `EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID` | 是 | RevenueCat Android 公钥 | 同上 |

**注意**:
- 这些是 **公钥** (Public Keys)，不是私钥
- RevenueCat 公钥可以安全地嵌入客户端应用
- 私钥 (Secret Key) 只在后端使用，见 `ENV_VARIABLES.md`

### Preview/Staging Build

Preview 构建可以使用相同的 Secrets，或者为 Staging 环境创建单独的 RevenueCat 项目

---

## 可选的 Secrets

### Google OAuth (如果启用 Web 登录)

```bash
eas secret:create --scope project --name EXPO_PUBLIC_GOOGLE_CLIENT_ID --value "your-client-id.apps.googleusercontent.com" --type string
```

**何时需要**:
- 如果移动应用支持 Google 登录
- 注意：这与后端的 `GOOGLE_CLIENT_ID` 可能不同

### Sentry DSN (如果启用错误追踪)

```bash
eas secret:create --scope project --name EXPO_PUBLIC_SENTRY_DSN --value "https://xxx@sentry.io/xxx" --type string
```

---

## Beta 测试模式配置

### Free Beta Mode (无需付费)

**场景**: 邀请朋友测试，暂不启用付费功能

**方法 1**: 在 `eas.json` 中配置 (推荐)
```json
{
  "build": {
    "preview": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://staging-api.clarity.app",
        "EXPO_PUBLIC_BILLING_ENABLED": "false"
      }
    }
  }
}
```

**方法 2**: 使用 EAS Secret (更灵活)
```bash
eas secret:create --scope project --name EXPO_PUBLIC_BILLING_ENABLED --value "false" --type string
eas secret:create --scope project --name EXPO_PUBLIC_BETA_MODE --value "true" --type string
```

**效果**:
- 隐藏所有付费相关的 UI
- 后端需要配置 `BETA_MODE=true` (见 `ENV_VARIABLES.md`)

---

## 命令速查

### 创建 Secret
```bash
# 基本格式
eas secret:create --scope project --name SECRET_NAME --value "secret_value" --type string

# 从文件读取 (适合多行内容)
eas secret:create --scope project --name SECRET_NAME --value "$(cat secret.txt)" --type string
```

### 查看已有 Secrets
```bash
# 列出所有 Secrets (不显示值)
eas secret:list

# 查看特定 Secret 的值 (需要权限)
eas secret:get --name EXPO_PUBLIC_REVENUECAT_API_KEY_IOS
```

### 更新 Secret
```bash
# 删除旧的
eas secret:delete --name SECRET_NAME

# 创建新的
eas secret:create --scope project --name SECRET_NAME --value "new_value" --type string
```

### 删除 Secret
```bash
eas secret:delete --name SECRET_NAME
```

---

## 与 `eas.json` 的关系

### `eas.json` 配置示例
```json
{
  "build": {
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.clarity.app"
      }
    }
  }
}
```

**合并逻辑**:
1. EAS Secrets 优先级 **高于** `eas.json` 中的 `env`
2. 如果 Secret 和 `env` 同时定义了同一个变量，使用 Secret 的值
3. 构建时两者会合并到最终的 `.env` 文件

---

## 构建流程

### 本地构建 (Development)
```bash
# 不使用 EAS Secrets，直接读取 .env.development
npx expo start
```

### 云端构建 (Preview/Production)
```bash
# Preview Build
eas build --profile preview --platform ios

# Production Build
eas build --profile production --platform all
```

**构建时发生了什么**:
1. EAS 从云端读取 Secrets
2. 与 `eas.json` 中的 `env` 合并
3. 生成临时 `.env` 文件
4. 运行 `expo build`
5. 删除临时 `.env` 文件

---

## RevenueCat 配置详解

### 获取 API Keys

1. 访问 [RevenueCat Dashboard](https://app.revenuecat.com)
2. 进入项目设置 → API Keys
3. 找到 **Public API Keys** (不是 Secret Keys)
4. 复制 iOS 和 Android 的公钥

### 设置 Secrets
```bash
# iOS
eas secret:create \
  --scope project \
  --name EXPO_PUBLIC_REVENUECAT_API_KEY_IOS \
  --value "appl_xxx" \
  --type string

# Android
eas secret:create \
  --scope project \
  --name EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID \
  --value "goog_xxx" \
  --type string
```

### 代码中使用
```typescript
// app/utils/revenuecat.ts
import Purchases from 'react-native-purchases';
import { Platform } from 'react-native';

const API_KEY = Platform.select({
  ios: process.env.EXPO_PUBLIC_REVENUECAT_API_KEY_IOS,
  android: process.env.EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID,
});

Purchases.configure({ apiKey: API_KEY });
```

---

## 安全最佳实践

### ✅ 安全做法

- 使用 `EXPO_PUBLIC_` 前缀只暴露必要的变量
- RevenueCat **公钥** 可以安全地嵌入客户端
- 定期轮换 API Keys (每 6 个月)
- 不同环境使用不同的 Keys (dev/staging/prod)

### ❌ 危险操作

- **永远不要** 将 RevenueCat **私钥** (Secret Key) 放入客户端
- **永远不要** 将 Stripe Secret Key 放入客户端
- **永远不要** 将 JWT Secret 放入客户端
- **永远不要** 将数据库密码放入客户端

**记住**:
- 客户端的所有 Secrets 都可以被逆向工程
- 只有后端的 Secrets 才是真正安全的

---

## 故障排查

### Secret 没有生效

**症状**: 构建时变量是 `undefined`

**解决步骤**:
1. 确认 Secret 名称正确 (区分大小写)
2. 确认使用了 `EXPO_PUBLIC_` 前缀
3. 清理缓存重新构建:
   ```bash
   eas build --profile production --platform ios --clear-cache
   ```

### RevenueCat 初始化失败

**症状**: `Error: Invalid API Key`

**检查清单**:
1. 确认复制的是 **Public Key** (不是 Secret Key)
2. 确认 iOS 用 `appl_` 开头的 Key
3. 确认 Android 用 `goog_` 开头的 Key
4. 确认 Secret 名称没有拼写错误

### 构建时找不到 Secret

**症状**: `Error: Environment variable not found`

**解决**:
```bash
# 检查 Secret 是否存在
eas secret:list

# 重新创建 Secret
eas secret:create --scope project --name SECRET_NAME --value "value" --type string
```

---

## 环境变量完整清单

### 客户端变量 (Mobile App)

| 变量名 | 来源 | 必需 | 说明 |
|--------|------|------|------|
| `EXPO_PUBLIC_API_URL` | `eas.json` | 是 | API 基础 URL |
| `EXPO_PUBLIC_REVENUECAT_API_KEY_IOS` | EAS Secret | 是* | RevenueCat iOS 公钥 |
| `EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID` | EAS Secret | 是* | RevenueCat Android 公钥 |
| `EXPO_PUBLIC_BILLING_ENABLED` | `eas.json` | 否 | 是否启用付费功能 |
| `EXPO_PUBLIC_BETA_MODE` | `eas.json` | 否 | 是否为 Beta 测试模式 |
| `EXPO_PUBLIC_GOOGLE_CLIENT_ID` | EAS Secret | 否 | Google OAuth (如果需要) |
| `EXPO_PUBLIC_SENTRY_DSN` | EAS Secret | 否 | Sentry 错误追踪 (如果需要) |

**\* 注意**: 只有当 `EXPO_PUBLIC_BILLING_ENABLED=true` 时才必需

### 后端变量 (API Server)

见 [`ENV_VARIABLES.md`](/Users/zhimingdeng/Documents/claude/clarity/docs/ENV_VARIABLES.md)

---

## 参考链接

- [EAS Secrets 官方文档](https://docs.expo.dev/build-reference/variables/)
- [RevenueCat API Keys 指南](https://www.revenuecat.com/docs/authentication)
- [Expo 环境变量最佳实践](https://docs.expo.dev/guides/environment-variables/)
- [Clarity 后端环境变量文档](./ENV_VARIABLES.md)

---

## Production Checklist

部署生产环境前，确认以下清单：

- [ ] `EXPO_PUBLIC_REVENUECAT_API_KEY_IOS` 已设置 (生产环境 Key)
- [ ] `EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID` 已设置 (生产环境 Key)
- [ ] `eas.json` 中的 `EXPO_PUBLIC_API_URL` 指向生产 API
- [ ] RevenueCat Dashboard 中的产品已配置 (见 RevenueCat 文档)
- [ ] 已在 App Store Connect / Google Play Console 中配置应用内购买
- [ ] 后端 `REVENUECAT_WEBHOOK_SECRET` 已配置
- [ ] 后端 `PAYMENTS_ENABLED=true`
- [ ] 后端 `BETA_MODE=false`

### Free Beta Checklist

部署免费 Beta 测试环境前，确认：

- [ ] `eas.json` 中的 `EXPO_PUBLIC_BILLING_ENABLED=false`
- [ ] 后端 `BETA_MODE=true`
- [ ] 后端 `PAYMENTS_ENABLED=false`
- [ ] 所有其他核心设置正确配置

---

**总结**: EAS Secrets 是存储 API Keys 的安全方式，但要记住客户端的任何东西都不是绝对安全的。敏感操作应该在后端验证
