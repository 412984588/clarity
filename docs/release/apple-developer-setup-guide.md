# Apple Developer Setup Guide

**Version**: 1.0
**Last Updated**: 2025-12-24
**Purpose**: 解除生产阻塞项 - Apple Developer 账号与 iOS 构建

---

## Purpose & Scope

本指南帮助完成 Clarity iOS 应用的 **Apple Developer Program 注册** 和 **App Store Connect 配置**，是 iOS 构建和 App Store 提交的必要前置步骤。

**解除的阻塞项**:
- ✅ Apple Developer Account 注册（$99/年）
- ✅ App Store Connect 访问权限
- ✅ iOS 证书与标识符配置
- ✅ TestFlight 内部测试能力
- ✅ Apple Sign-In 生产凭据

**不包含**:
- ❌ Expo EAS Build 配置（见 EAS Preview 文档）
- ❌ 具体构建命令（见 Mobile CI/CD 文档）
- ❌ App Store 提交流程（见 Store Submission Checklist）

---

## Account Types Comparison

在注册前，需要选择账号类型：

| 特性 | Individual (个人) | Organization (组织) |
|------|------------------|---------------------|
| **年费** | $99 USD | $99 USD |
| **审核时间** | 即时（Apple ID 验证） | 1-3 工作日（需验证法人实体） |
| **App 发布者名称** | 个人姓名 | 公司名称 |
| **团队协作** | ❌ 仅自己 | ✅ 可添加多人（不同角色） |
| **适用场景** | 个人开发者、快速测试 | 公司产品、团队开发 |
| **法人证明** | ❌ 不需要 | ✅ 需要（DUNS、营业执照等） |
| **推荐** | ⭐ 推荐（快速启动） | ✅ 长期运营（如有公司） |

**Decision**: [ ] 选择账号类型：`Individual` / `Organization`

**建议**:
- **如果 Clarity 是个人项目或希望快速上线**: 选择 **Individual**
- **如果 Clarity 有注册公司且需要团队协作**: 选择 **Organization**
- **可以从 Individual 转为 Organization**（后续升级，需重新审核）

---

## Prerequisites

根据所选账号类型，准备以下材料：

### For Individual Account

| 项目 | 说明 | 示例 |
|------|------|------|
| **Apple ID** | 已激活的 Apple ID（建议独立创建，不用个人主账号） | developer@clarity.app |
| **信用卡** | Visa / Mastercard / American Express | 需支持国际支付 |
| **电话号码** | 用于接收验证码（可用中国号码） | +1-555-123-4567 / +86-138-xxxx-xxxx |
| **身份证明** | Apple 可能要求提供身份证或驾照照片 | 准备扫描件或照片 |

---

### For Organization Account

| 项目 | 说明 | 获取方式 |
|------|------|----------|
| **Apple ID** | 公司主账号（法人或授权代表的 Apple ID） | 创建新 Apple ID |
| **Legal Entity Name** | 公司法定名称（与营业执照完全一致） | 营业执照 |
| **D-U-N-S Number** | 邓白氏编码（全球企业唯一标识符） | https://www.dnb.com/duns-number.html |
| **公司网站** | 公司官方网站（域名需与公司名称相关） | www.clarity-company.com |
| **法人联系信息** | 法人姓名、职位、邮箱、电话 | CEO / CTO |
| **公司地址** | 注册地址（与营业执照一致） | 完整邮寄地址 |
| **信用卡** | 公司信用卡或法人信用卡 | Visa / Mastercard |

**⚠️ D-U-N-S Number 申请**:
- 免费申请，但需 **5-30 个工作日**审核
- 访问: https://developer.apple.com/enroll/duns-lookup/
- Apple 提供快速通道（通常 1-2 周）

---

## Enrollment Steps

### Phase 1: Prepare Apple ID

**预计时间**: 5-10 分钟

#### Step 1.1: 创建或准备 Apple ID

**建议**: 创建独立的 Apple ID 用于开发者账号（不用个人 iCloud 账号）

1. 访问 https://appleid.apple.com/
2. 点击 "Create Your Apple ID"
3. 填写信息:
   - Email: `developer@clarity.app`（推荐使用公司域名邮箱）
   - Password: 强密码（至少 8 位，包含大小写字母和数字）
   - Phone: 用于接收验证码
   - Security Questions: 选择并记住答案
4. 验证邮箱（查收验证邮件并点击链接）
5. 启用 **Two-Factor Authentication** (2FA)（必需）:
   - 设置 → 密码与安全 → 双重认证
   - 添加受信任设备（iPhone / iPad）

---

#### Step 1.2: 配置 Payment Method

1. 登录 Apple ID (https://appleid.apple.com)
2. 进入 "Payment and Shipping"
3. 添加信用卡信息:
   - Card Number
   - Expiration Date
   - CVV
   - Billing Address（账单地址）
4. 保存并验证

---

### Phase 2: Enroll in Apple Developer Program

**预计时间**: Individual (15 分钟) / Organization (30 分钟 + 审核等待)

#### Step 2.1: 开始注册流程

1. 访问 https://developer.apple.com/programs/enroll/
2. 点击 "Start Your Enrollment"
3. 使用准备好的 Apple ID 登录
4. 选择账号类型:
   - [ ] **Enroll as an Individual**
   - [ ] **Enroll as an Organization**

---

#### Step 2.2a: Individual Enrollment (个人账号)

1. **Agree to Apple Developer Agreement**
   - 阅读并勾选同意条款

2. **Verify Identity**
   - Apple 会验证你的 Apple ID 信息
   - 可能要求提供额外身份证明（驾照、护照照片）

3. **Complete Purchase**
   - 费用: $99 USD/年
   - 使用已添加的信用卡支付
   - 确认订单

4. **Activation**
   - ✅ **即时生效**（支付成功后 5-30 分钟）
   - 收到确认邮件: "Welcome to the Apple Developer Program"

---

#### Step 2.3b: Organization Enrollment (组织账号)

1. **Provide Organization Information**
   - Legal Entity Name: `Clarity Inc.` (与营业执照完全一致)
   - D-U-N-S Number: `08-xxx-xxxx` (提前申请)
   - Company Website: `https://www.clarity.app`
   - Phone Number: 公司座机或法人手机
   - Address: 注册地址

2. **Verify Legal Entity**
   - Apple 会验证 D-U-N-S Number 和公司信息
   - 可能通过电话联系法人进行确认

3. **Provide Authority Information**
   - Legal Entity Representative (法人代表):
     - Name: 法人姓名
     - Title: CEO / CTO
     - Email: 法人邮箱
     - Phone: 法人电话
   - Apple 会发送验证邮件到法人邮箱

4. **Upload Supporting Documents** (如需要)
   - 营业执照扫描件
   - 法人身份证明
   - 授权委托书（如申请人非法人）

5. **Complete Purchase**
   - 费用: $99 USD/年
   - 使用公司信用卡或法人信用卡支付

6. **Wait for Review**
   - ⏱️ **审核时间**: 1-3 个工作日（通常 1 天）
   - 可能收到 Apple 的电话或邮件询问

7. **Activation**
   - 审核通过后收到确认邮件
   - 账号激活，可访问 App Store Connect

---

### Phase 3: Access App Store Connect

**预计时间**: 5-10 分钟

#### Step 3.1: 首次登录

1. 访问 https://appstoreconnect.apple.com/
2. 使用 Apple Developer 账号登录
3. 完成初始设置:
   - 同意 App Store Connect 协议
   - 配置税务信息（初次可跳过，提交 App 前必填）
   - 配置银行信息（收取 App 收入，提交 App 前必填）

---

#### Step 3.2: 设置团队角色 (仅 Organization)

**如果是 Organization 账号**，可添加团队成员：

1. 进入 "Users and Access"
2. 点击 "+" 添加用户
3. 输入成员的 Apple ID
4. 分配角色:
   - **Admin**: 完全权限（管理用户、证书、App）
   - **Developer**: 开发权限（证书、Provisioning Profile）
   - **App Manager**: App 管理权限（上传构建、管理元数据）
   - **Marketing**: 仅查看和编辑 App 元数据
   - **Customer Support**: 查看评论和崩溃报告
5. 发送邀请（成员收到邮件后接受）

**推荐角色分配**:
- CTO / Tech Lead: **Admin**
- 开发人员: **Developer**
- 产品经理: **App Manager**

---

### Phase 4: Certificates & Identifiers Overview

**预计时间**: 不需要手动操作（EAS Build 自动处理）

Clarity 使用 **Expo EAS Build**，证书和 Provisioning Profile 会自动管理。但了解以下概念有助于排查问题：

#### 4.1: App ID (Identifier)

**What**: App 的唯一标识符

**Example**: `com.clarity.app`

**Created by**: EAS Build 自动创建（或手动在 developer.apple.com → Certificates, Identifiers & Profiles → Identifiers）

---

#### 4.2: Certificates

**What**: 用于签名 App 的证书

**Types**:
- **Development Certificate**: 用于开发和调试
- **Distribution Certificate**: 用于 App Store 提交和 TestFlight

**Created by**: EAS Build 自动创建并管理

---

#### 4.3: Provisioning Profiles

**What**: 关联 App ID、证书和设备的配置文件

**Types**:
- **Development Profile**: 用于真机调试
- **Ad Hoc Profile**: 用于直接分发（最多 100 台设备）
- **App Store Profile**: 用于 App Store 提交

**Created by**: EAS Build 自动创建并管理

---

#### 4.4: Manual Setup (仅在 EAS Build 失败时)

**If EAS Build fails to create certificates**:

1. 访问 https://developer.apple.com/account/resources/identifiers/list
2. 点击 "+" 创建 App ID:
   - Description: `Clarity`
   - Bundle ID: `com.clarity.app` (Explicit)
   - Capabilities: 勾选需要的能力（Push Notifications, Sign in with Apple, In-App Purchase）
3. 访问 https://developer.apple.com/account/resources/certificates/list
4. 点击 "+" 创建 Distribution Certificate:
   - 选择 "iOS Distribution (App Store and Ad Hoc)"
   - 上传 CSR 文件（在 Mac 上用 Keychain Access 生成）
   - 下载证书并双击安装到 Keychain

**⚠️ 通常不需要手动操作**，EAS Build 会自动处理。

---

### Phase 5: Enable Apple Sign-In (Production)

**预计时间**: 10-15 分钟

Clarity 使用 **Sign in with Apple** 作为登录方式之一，需要配置生产环境凭据。

#### Step 5.1: 创建 Services ID

1. 访问 https://developer.apple.com/account/resources/identifiers/list/serviceId
2. 点击 "+" 创建 Services ID
3. 填写信息:
   - Description: `Clarity Sign in with Apple`
   - Identifier: `com.clarity.app.signin` (推荐格式)
4. 勾选 "Sign in with Apple"
5. 点击 "Configure"
6. 配置 Web Authentication:
   - Primary App ID: 选择 `com.clarity.app`
   - Domains and Subdomains: `clarity.app`, `api.clarity.app`
   - Return URLs: `https://api.clarity.app/auth/apple/callback`
7. 保存并继续

---

#### Step 5.2: 创建 Private Key

1. 访问 https://developer.apple.com/account/resources/authkeys/list
2. 点击 "+" 创建 Key
3. 填写信息:
   - Key Name: `Clarity Apple Sign-In Key`
   - 勾选 "Sign in with Apple"
   - 点击 "Configure" 并选择 Primary App ID: `com.clarity.app`
4. 点击 "Continue" 并 "Register"
5. **下载 Private Key** (`.p8` 文件)
   - ⚠️ **只能下载一次**，请妥善保存
   - 记录 **Key ID**（10 个字符，如 `ABC123DEFG`）

---

#### Step 5.3: 配置环境变量

将以下信息添加到生产环境变量（见 `docs/ENV_VARIABLES.md`）:

```bash
APPLE_CLIENT_ID=com.clarity.app.signin       # Services ID
APPLE_TEAM_ID=XXXXXXXXXX                     # Team ID (在 developer.apple.com 右上角)
APPLE_KEY_ID=ABC123DEFG                      # Private Key ID
APPLE_PRIVATE_KEY=<.p8 文件内容>             # Private Key 内容（完整复制）
```

**How to find Team ID**:
1. 访问 https://developer.apple.com/account
2. 右上角 "Membership" → Team ID (10 个字符)

---

## Common Blockers & Solutions

### Blocker 1: D-U-N-S Number Delays (Organization Only)

**问题**: D-U-N-S Number 申请需要 5-30 工作日

**解决方案**:
- **Option A**: 使用 Apple 快速通道（通常 1-2 周，仍需等待）
- **Option B**: 先用 **Individual Account** 注册（$99），快速启动，后续转为 Organization
- **Option C**: 提前申请 D-U-N-S Number（访问 https://www.dnb.com/duns-number.html）

**推荐**: **Option B**（先 Individual，后升级）

---

### Blocker 2: Payment Method Declined

**问题**: 信用卡支付被拒

**原因**: 银行拒绝国际支付 / 卡片额度不足 / 地址不匹配

**解决方案**:
- 联系银行开通国际支付功能
- 换一张信用卡（Visa/Mastercard 通常支持更好）
- 确认 Billing Address 与卡片账单地址完全一致

---

### Blocker 3: Account Under Review (Organization)

**问题**: 提交 Organization 注册后，迟迟未收到审核结果

**原因**: Apple 需要人工审核法人实体信息

**解决方案**:
- 检查邮箱（包括垃圾邮件）是否有 Apple 邮件
- 等待 1-3 个工作日
- 如超过 5 个工作日无回复，联系 Apple Developer Support: https://developer.apple.com/contact/

---

### Blocker 4: Two-Factor Authentication Issues

**问题**: 无法接收 2FA 验证码

**原因**: 受信任设备离线 / 电话号码无效

**解决方案**:
- 确保至少一台 Apple 设备（iPhone/iPad/Mac）登录了该 Apple ID 并联网
- 添加备用电话号码（Apple ID 设置 → 受信任电话号码）
- 使用恢复密钥（Apple ID 设置 → 安全性 → 恢复密钥）

---

## Time Estimates

| 阶段 | Individual | Organization | 依赖 |
|------|-----------|--------------|------|
| **Apple ID 准备** | 10 分钟 | 10 分钟 | 无 |
| **D-U-N-S Number 申请** | N/A | **5-30 工作日** | 公司法人信息 |
| **Enrollment 提交** | 15 分钟 | 30 分钟 | Apple ID + Payment |
| **审核等待** | **即时** | **1-3 工作日** | Apple 人工审核 |
| **App Store Connect 配置** | 10 分钟 | 10 分钟 | Account Active |
| **Apple Sign-In 配置** | 15 分钟 | 15 分钟 | Account Active |
| **总计（最快）** | **50 分钟** | **1 小时** + 审核等待 | |
| **总计（保守）** | **1 小时** | **1 小时** + **1-3 工作日审核** + **D-U-N-S 等待** | |

**推荐时间规划**:
- **Individual**: 当天完成
- **Organization (有 D-U-N-S)**: 1-3 工作日
- **Organization (无 D-U-N-S)**: **1-4 周**

---

## Completion Criteria

完成以下所有检查项后，Apple Developer 配置即为完成：

### Enrollment Checklist

- [ ] **1. Apple ID 已创建**（独立开发者账号）
- [ ] **2. Two-Factor Authentication 已启用**
- [ ] **3. Payment Method 已添加**（信用卡）
- [ ] **4. Apple Developer Program 已注册**（Individual / Organization）
- [ ] **5. 年费 $99 已支付**
- [ ] **6. Enrollment 已通过审核**（Organization 需等待）

---

### App Store Connect Checklist

- [ ] **7. App Store Connect 可访问**（https://appstoreconnect.apple.com）
- [ ] **8. 初始协议已同意**
- [ ] **9. Team 角色已配置**（如 Organization 有多人）

---

### Certificates & Identifiers Checklist (EAS Build 自动处理)

- [ ] **10. App ID 已创建**（com.clarity.app）或由 EAS 自动创建
- [ ] **11. Distribution Certificate 已生成**（或由 EAS 自动生成）
- [ ] **12. Provisioning Profile 已创建**（或由 EAS 自动生成）

---

### Apple Sign-In Checklist

- [ ] **13. Services ID 已创建**（com.clarity.app.signin）
- [ ] **14. Private Key 已下载**（.p8 文件已保存）
- [ ] **15. 环境变量已配置**（APPLE_CLIENT_ID, APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY）
- [ ] **16. Return URL 已配置**（https://api.clarity.app/auth/apple/callback）

---

### TestFlight Checklist (Optional for Beta Testing)

- [ ] **17. TestFlight 可访问**（App Store Connect → TestFlight）
- [ ] **18. Internal Testers 已添加**（团队成员可测试）
- [ ] **19. External Testers 可邀请**（朋友/测试用户）

---

### Final Validation

- [ ] **20. EAS Build (iOS) 可成功构建**
  - 测试: `eas build --platform ios --profile preview`
  - 预期: Build 成功，无证书错误

- [ ] **21. TestFlight Build 可上传**
  - 测试: `eas submit --platform ios`
  - 预期: Build 出现在 App Store Connect → TestFlight

- [ ] **22. Apple Sign-In 在生产环境可用**
  - 测试: 前端调用后端 `/auth/apple/login`
  - 预期: 成功跳转到 Apple 授权页面

---

## Related Documents

### Prerequisites

- [Launch Dependencies](launch-dependencies.md) - 所有生产依赖项追踪
- [Store Privacy Answers](store-privacy-answers.md) - App Store 隐私问卷答案

### Next Steps (After Apple Developer Setup)

- [EAS Preview](eas-preview.md) - iOS 构建配置（EAS Build）
- [Store Submission Checklist](store-submission-checklist.md) - App Store 提交清单
- [TestFlight Beta Testing](#) - TestFlight 内部测试指南

### Related Guides

- [Domain & Hosting Setup Guide](domain-hosting-setup-guide.md) - 域名与托管阻塞项解除
- [Prod Preflight](prod-preflight.md) - 生产部署预检清单

---

**完成此指南后，您将解除 "Apple Developer Account" 阻塞项，并可进行 iOS 构建、TestFlight 测试和 App Store 提交。**
