# Epic 7: Launch Readiness - Task Breakdown

## Task 1: 移动端环境变量配置

### 1.1 创建环境变量文件

**Files**:
- `clarity-mobile/.env.development`
- `clarity-mobile/.env.staging`
- `clarity-mobile/.env.production`
- `clarity-mobile/.env.example`

**Commands**:
```bash
cd clarity-mobile

# 创建环境文件
echo 'EXPO_PUBLIC_API_URL=http://localhost:8000' > .env.development
echo 'EXPO_PUBLIC_API_URL=https://staging-api.clarity.app' > .env.staging
echo 'EXPO_PUBLIC_API_URL=https://api.clarity.app' > .env.production
echo 'EXPO_PUBLIC_API_URL=http://localhost:8000' > .env.example
```

**Verification**:
```bash
ls -la .env.*
cat .env.development
```

### 1.2 创建动态配置文件

**File**: `clarity-mobile/app.config.ts`

**Content**:
```typescript
import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: 'clarity-mobile',
  slug: 'clarity-mobile',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'light',
  newArchEnabled: true,
  splash: {
    image: './assets/splash-icon.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff',
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.clarity.mobile',
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#ffffff',
    },
    package: 'com.clarity.mobile',
    edgeToEdgeEnabled: true,
    predictiveBackGestureEnabled: false,
  },
  web: {
    favicon: './assets/favicon.png',
  },
  plugins: [
    'expo-web-browser',
    'expo-secure-store',
    'expo-router',
    'expo-localization',
  ],
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000',
  },
});
```

**Verification**:
```bash
npx expo config --type public | grep apiUrl
```

### 1.3 更新 .gitignore

**File**: `clarity-mobile/.gitignore`

**Add**:
```
# Environment files (keep .env.example)
.env.development
.env.staging
.env.production
.env.local
.env
```

**Verification**:
```bash
grep ".env" .gitignore
```

---

## Task 2: 更新 docs/setup.md

**File**: `docs/setup.md`

**Add Section**:
```markdown
## iOS 本地调试

### 环境要求
- macOS 12+
- Xcode 14+ (从 App Store 安装)
- CocoaPods (`sudo gem install cocoapods`)

### 模拟器调试
\`\`\`bash
cd clarity-mobile
npx expo start --ios
\`\`\`

### 真机调试
1. 注册 Apple Developer Account
2. 在 Xcode 中配置 Signing & Capabilities
3. 连接 iPhone，运行 `npx expo run:ios --device`

## Android 本地调试

### 环境要求
- Android Studio (最新稳定版)
- Android SDK (API 33+)
- JDK 17+

### 模拟器调试
\`\`\`bash
cd clarity-mobile
npx expo start --android
\`\`\`

### 真机调试
1. 手机开启 "开发者选项" → "USB 调试"
2. 连接 USB，运行 `npx expo run:android --device`

## 环境变量配置

| 环境 | 文件 | API URL |
|------|------|---------|
| dev | `.env.development` | `http://localhost:8000` |
| staging | `.env.staging` | `https://staging-api.clarity.app` |
| prod | `.env.production` | `https://api.clarity.app` |
```

**Verification**:
```bash
grep -c "iOS 本地调试" docs/setup.md
```

---

## Task 3: 增强 EAS Build Profiles

**File**: `clarity-mobile/eas.json`

**Content**:
```json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "http://localhost:8000"
      }
    },
    "preview": {
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "https://staging-api.clarity.app"
      }
    },
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.clarity.app"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

**Verification**:
```bash
cat eas.json | jq '.build.production.env'
```

---

## Task 4: 后端 Health 端点增强

**File**: `clarity-api/app/main.py`

**Add**:
```python
@app.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe - 检查数据库连接"""
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe - 检查进程存活"""
    return {"live": True}
```

**Verification**:
```bash
cd clarity-api
poetry run pytest -v
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

---

## Task 5: 移动端 Error Boundary

**File**: `clarity-mobile/components/ErrorBoundary.tsx`

**Content**:
```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

const ERROR_LOG_KEY = '@clarity/error_log';

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.logError(error, errorInfo);
  }

  async logError(error: Error, errorInfo: ErrorInfo) {
    try {
      const errorLog = {
        timestamp: new Date().toISOString(),
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      };
      const existing = await AsyncStorage.getItem(ERROR_LOG_KEY);
      const logs = existing ? JSON.parse(existing) : [];
      logs.push(errorLog);
      // 只保留最近 10 条
      const trimmed = logs.slice(-10);
      await AsyncStorage.setItem(ERROR_LOG_KEY, JSON.stringify(trimmed));
    } catch {
      // 静默失败
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <View style={styles.container}>
          <Text style={styles.title}>Something went wrong</Text>
          <Text style={styles.message}>{this.state.error?.message}</Text>
          <Pressable style={styles.button} onPress={this.handleRetry}>
            <Text style={styles.buttonText}>Try Again</Text>
          </Pressable>
        </View>
      );
    }
    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f8fafc',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  message: {
    fontSize: 14,
    color: '#64748b',
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#1d4ed8',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
```

**Verification**:
```bash
npm run lint
npx tsc --noEmit
```

---

## Task 6: 合规文档占位

### 6.1 Release Checklist

**File**: `docs/release/release-checklist.md`

**Content**: 上架清单模板

### 6.2 Privacy Policy

**File**: `docs/release/privacy.md`

**Content**: 隐私政策模板

### 6.3 Support Page

**File**: `docs/release/support.md`

**Content**: 支持页面模板

**Verification**:
```bash
ls docs/release/
```

---

## Task 7: 验收脚本

**File**: `scripts/verify-release.sh`

**Content**:
```bash
#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║     Clarity Release Verification       ║"
echo "╚════════════════════════════════════════╝"

ROOT_DIR=$(dirname "$0")/..
cd "$ROOT_DIR"

echo ""
echo "=== [1/5] Backend Lint ==="
cd clarity-api
poetry run ruff check .
echo "✅ Ruff passed"

echo ""
echo "=== [2/5] Backend Type Check ==="
poetry run mypy app --ignore-missing-imports
echo "✅ Mypy passed"

echo ""
echo "=== [3/5] Backend Tests ==="
poetry run pytest -v
echo "✅ Pytest passed"

echo ""
echo "=== [4/5] Mobile Lint ==="
cd ../clarity-mobile
npm run lint
echo "✅ ESLint passed"

echo ""
echo "=== [5/5] Mobile Type Check ==="
npx tsc --noEmit
echo "✅ TypeScript passed"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     ✅ ALL CHECKS PASSED               ║"
echo "╚════════════════════════════════════════╝"

echo ""
echo "Optional: Run these manually if server is running:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/health/ready"
echo "  curl http://localhost:8000/health/live"
```

**Commands**:
```bash
chmod +x scripts/verify-release.sh
./scripts/verify-release.sh
```

**Verification**:
```bash
./scripts/verify-release.sh
```

---

## Task 8: 更新 PROGRESS.md

**File**: `docs/PROGRESS.md`

**Add**:
```markdown
### [YYYY-MM-DD HH:mm] - Epic 7: Launch Readiness

- [x] **环境配置**: 三环境变量文件 (dev/staging/prod)
- [x] **动态配置**: app.config.ts 替代 app.json
- [x] **EAS Build**: 增强构建配置，环境变量注入
- [x] **Health 端点**: /health/ready, /health/live
- [x] **Error Boundary**: 移动端错误捕获组件
- [x] **合规文档**: release-checklist, privacy, support
- [x] **验收脚本**: scripts/verify-release.sh
- [x] **setup.md**: 添加 iOS/Android 调试说明

> **新增文件**:
> - clarity-mobile/.env.*, app.config.ts
> - clarity-mobile/components/ErrorBoundary.tsx
> - docs/release/*.md
> - scripts/verify-release.sh

> **测试验证**:
> - ./scripts/verify-release.sh ✅
```

---

## 执行顺序

| 顺序 | Task | 依赖 |
|------|------|------|
| 1 | Task 1 (环境变量) | 无 |
| 2 | Task 2 (setup.md) | 无 |
| 3 | Task 3 (eas.json) | Task 1 |
| 4 | Task 4 (Health 端点) | 无 |
| 5 | Task 5 (ErrorBoundary) | 无 |
| 6 | Task 6 (合规文档) | 无 |
| 7 | Task 7 (验收脚本) | Task 1-6 |
| 8 | Task 8 (PROGRESS.md) | Task 7 |

---

## 最终验证

```bash
# 完整验收
./scripts/verify-release.sh

# 期望输出: ✅ ALL CHECKS PASSED
```
