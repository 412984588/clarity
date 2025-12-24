# Free Beta Invite Templates

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose

This document provides email and message templates for recruiting and communicating with Free Beta testers. Use these templates to maintain consistent, professional, and friendly communication throughout the beta testing cycle.

**Target Audience**: Friends, early adopters, and internal team members willing to test Clarity before public launch.

**使用场景**:
- 招募测试者 (Recruiting testers)
- 欢迎新测试者 (Onboarding new testers)
- 提醒参与测试 (Reminding testers to participate)
- 收集反馈 (Collecting feedback)
- 跟进问题 (Following up on issues)
- 结束测试 (Wrapping up beta)

---

## Audience Segments

根据不同受众，调整沟通风格和技术细节程度：

| Segment | Description | Tone | Technical Detail |
|---------|-------------|------|------------------|
| **朋友 (Friends)** | 非技术背景的朋友 | 亲切、口语化 | 低 - 避免技术术语 |
| **技术同学 (Tech Friends)** | 有技术背景的朋友或同事 | 专业、直接 | 高 - 可包含技术细节 |
| **非技术用户 (Non-tech Users)** | 无技术背景的早期用户 | 简单、清晰 | 无 - 纯白话解释 |

**建议**:
- 根据受众调整模板内容
- 非技术用户使用"安装"而非"部署APK"
- 技术用户可以提供 Build ID、API 端点等信息

---

## Templates

### Template 1: Invite (First Ask)

#### For Friends (朋友版)

**Subject**: 帮我测试一下新 App？🙏

**Message**:
```
嗨 [Name]，

我最近做了一个 App 叫 Clarity，是一个 AI 助手，帮人理清思路、解决问题的。现在快做好了，想找几个朋友先试试看，能帮我测一下吗？

**你需要做的**：
- 花 20-30 分钟体验一下（随便什么时候都行）
- 告诉我哪里好用、哪里不好用
- 遇到 Bug 或者用不了的地方跟我说一声

**你会得到**：
- 免费使用所有功能
- 提前体验还没上线的版本
- 未来可能有的优惠（TBD）

**需要什么设备**：
- Android 手机（暂时没有 iOS，抱歉！）
- 能上网就行

如果你有空帮忙，我把安装链接和使用指南发给你。大概 2-3 周测试期，不着急，有空就试试。

谢谢！🙏

[Your Name]

P.S. 不用担心隐私问题，你的数据只有你自己能看到，我这边只会收集匿名的使用情况（比如"有多少人完成了流程"这种）。
```

**Placeholders**:
- `[Name]` - 测试者名字
- `[Your Name]` - 你的名字

---

#### For Tech Friends (技术版)

**Subject**: Clarity Free Beta 测试邀请 - Android APK

**Message**:
```
Hi [Name],

I'm launching a Free Beta for Clarity, an AI-powered problem-solving assistant built with React Native + FastAPI. Looking for early testers to validate core features before production.

**Tech Stack**:
- Mobile: React Native + Expo
- Backend: FastAPI + PostgreSQL
- AI: OpenAI/Claude integration

**What's Included in Beta**:
✅ 5-step Solve flow (Receive → Clarify → Reframe → Options → Commit)
✅ Emotion detection with visual feedback
✅ Multi-language support (EN/ES/ZH)
❌ Payments disabled (Free Beta mode)
❌ iOS not available (requires Apple Dev Account)

**What I Need**:
- Install Android APK (preview build via Expo)
- Test core features for 20-30 minutes
- Report bugs via [Bug Template](bug-report-template.md)
- Fill out [Feedback Form](beta-feedback-form.md)

**Timeline**: 2-3 weeks, flexible

**Android APK**:
- Download: [Will provide link after acceptance]
- Build ID: 88df477f-4862-41ac-9c44-4134aa2b67e2

Interested? Reply with "Yes" and I'll send the APK link + tester guide.

Thanks!
[Your Name]
```

**Placeholders**:
- `[Name]` - Tester name
- `[Your Name]` - Your name

---

### Template 2: Acceptance / Welcome

#### Subject: Welcome to Clarity Beta! 🎉

**Message**:
```
Hi [Name],

谢谢你愿意帮忙测试！这是你需要的所有东西：

**📱 Android APK 下载**:
[APK Download Link]

**📖 使用指南**:
[Link to Free Beta Tester Guide](free-beta-tester-guide.md)

**📝 反馈表单**:
[Link to Beta Feedback Form](beta-feedback-form.md)

**🐛 Bug 报告模板**:
[Link to Bug Report Template](bug-report-template.md)

**安装步骤**:
1. 点击上面的 APK 链接，用手机下载
2. 下载后点击文件安装（可能需要开启"允许未知来源"）
3. 打开 App，注册账号（邮箱或 Google 登录都可以）
4. 试着完成一次完整的 Solve 流程

**测试重点**:
- 核心流程能不能跑通
- 有没有卡顿或崩溃
- 哪里用起来别扭或者不明白

**遇到问题怎么办**:
- 随时联系我：[Your Email] 或 [Your Phone]
- 或者填写 Bug 报告模板发给我

**大概要测多久**:
- 随便你，有空就试试
- 理想情况：1-2 周内能试完最好

再次感谢！有任何问题随时找我。

Best,
[Your Name]
```

**Placeholders**:
- `[Name]` - Tester name
- `[APK Download Link]` - https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk
- `[Your Email]` - Your contact email
- `[Your Phone]` - Your phone number (optional)
- `[Your Name]` - Your name

---

### Template 3: Reminder (Day 3)

#### Subject: Clarity Beta - 有空试试看吗？😊

**Message**:
```
Hi [Name],

三天前给你发了 Clarity Beta 测试邀请，不知道你有没有空看一下？

**如果已经试过了**:
- 太好了！有什么反馈吗？好的坏的都想听听
- 可以填一下这个[反馈表单](beta-feedback-form.md)，5 分钟搞定

**如果还没试**:
- 没关系！不着急，有空再说
- 这是 APK 下载链接：[APK Link]
- 这是使用指南：[Tester Guide Link]

**需要帮助吗**:
- 安装遇到问题？我可以远程帮你
- 不知道怎么测？可以只试一下基本功能就行

谢谢！

[Your Name]
```

**Placeholders**:
- `[Name]` - Tester name
- `[APK Link]` - APK download URL
- `[Tester Guide Link]` - Free Beta Tester Guide URL
- `[Your Name]` - Your name

---

### Template 4: Reminder (Day 7)

#### Subject: Clarity Beta - 最后提醒一次 🙏

**Message**:
```
Hi [Name],

一周前邀请你测试 Clarity，想最后确认一下你还有没有兴趣？

**如果还想测**:
- APK 链接在这里：[APK Link]
- 使用指南在这里：[Tester Guide Link]
- 有空的时候试试就行，不强求

**如果没空或者不感兴趣**:
- 完全没问题！谢谢你之前的关注
- 回复"不测了"我就不再打扰你了

**如果已经测过了**:
- 太感谢了！记得填一下[反馈表单](beta-feedback-form.md)
- 或者直接回复告诉我你的想法

不管怎样，谢谢你！

[Your Name]
```

**Placeholders**:
- `[Name]` - Tester name
- `[APK Link]` - APK download URL
- `[Tester Guide Link]` - Free Beta Tester Guide URL
- `[Your Name]` - Your name

---

### Template 5: Thank You + Feedback Request

#### Subject: 谢谢你测试 Clarity！需要你的反馈 📝

**Message**:
```
Hi [Name],

看到你已经试过 Clarity 了，太感谢了！

**现在需要你帮个小忙**:
请花 5-10 分钟填一下这个[反馈表单](beta-feedback-form.md)，告诉我：
- 哪里好用 / 哪里不好用
- 遇到了什么 Bug
- 有什么建议

**为什么这个很重要**:
- 你的反馈会直接影响正式版的功能
- 我需要知道哪些地方要改进
- 如果大家都觉得某个功能有问题，我会优先修

**填完表单后**:
- 你可以继续用 App（会一直免费）
- 或者卸载也完全 OK
- 后面有新版本我会再通知你

**额外奖励（可选）**:
- 如果你愿意，可以写一段话推荐 Clarity
- 我可能会用在网站或宣传材料上（会署名或匿名，你选）

再次感谢你的帮助！🙏

[Your Name]

P.S. 表单链接：[Feedback Form Link]
```

**Placeholders**:
- `[Name]` - Tester name
- `[Feedback Form Link]` - Beta Feedback Form URL
- `[Your Name]` - Your name

---

### Template 6: Issue Follow-up

#### Subject: Re: [Bug Title] - 进展更新

**Message**:
```
Hi [Name],

关于你报告的问题 "[Bug Title]"，有进展了：

**问题描述**:
[简短重述 Bug]

**当前状态**:
- [x] 已确认问题
- [x] 已找到原因
- [ ] 修复中 / [x] 已修复

**解决方案**:
[解释你怎么修的，用人话]

**下一步**:
- 如果已修复：请下载新版本 APK [New APK Link] 再试试
- 如果还在修：预计 [Timeline] 会修好

**需要你做什么**:
- 如果方便，帮我验证一下新版本是不是修好了
- 如果还有问题，再告诉我一声

谢谢你报告这个 Bug！

[Your Name]
```

**Placeholders**:
- `[Name]` - Tester name
- `[Bug Title]` - Bug title from report
- `[Timeline]` - Expected fix timeline
- `[New APK Link]` - New APK download link (if fixed)
- `[Your Name]` - Your name

---

### Template 7: Wrap-up / Exit Survey

#### Subject: Clarity Beta 结束 - 谢谢你的参与！🎉

**Message**:
```
Hi [Name],

Clarity 的 Free Beta 测试已经结束了，非常感谢你这段时间的帮助！

**成果总结**:
- 总共 [X] 位测试者参与
- 收到 [Y] 条反馈
- 修复了 [Z] 个 Bug
- 你的贡献：[具体贡献，比如"报告了 3 个 Bug"或"完成了完整测试"]

**下一步计划**:
- 我会根据大家的反馈继续改进
- 预计 [Timeline] 正式上线
- 到时候会第一时间通知你

**最后一个小请求**:
如果你还没填[退出调查](exit-survey-link)，麻烦花 3 分钟填一下：
- 整体体验打几分？
- 会推荐给朋友吗？
- 有什么最后的建议？

**作为感谢**:
- 正式上线后，你会获得 [优惠/特权，TBD]
- 如果你愿意，可以把你列为"Early Tester"（会在 About 页面展示）

再次感谢你的支持！希望 Clarity 能帮到更多人。

Stay in touch,
[Your Name]

P.S. 如果后面还想继续测试新功能，回复"继续参与"，我会拉你进长期测试组。
```

**Placeholders**:
- `[Name]` - Tester name
- `[X]` - Total testers count
- `[Y]` - Total feedback count
- `[Z]` - Bugs fixed count
- `[Timeline]` - Expected launch date
- `[Your Name]` - Your name

---

## Do & Don't

### Do (✅ 应该这样做)

| Guideline | Example |
|-----------|---------|
| **Be personal** | "Hi John" instead of "Dear User" |
| **Be specific** | "Fill out the 5-minute feedback form" instead of "Send feedback" |
| **Be grateful** | Always say "Thank you" and acknowledge their time |
| **Be transparent** | Explain what you'll use their feedback for |
| **Be responsive** | Reply to tester questions within 24 hours |
| **Be flexible** | "No rush, test when you have time" |
| **Provide clear next steps** | "Click this link → Install → Open app" |
| **Use simple language for non-tech users** | "Install the app" instead of "Deploy the APK" |

### Don't (❌ 不要这样做)

| Mistake | Why It's Bad | Fix |
|---------|--------------|-----|
| **Don't spam** | Sending reminders every day | Max 2-3 reminders over 2 weeks |
| **Don't assume technical knowledge** | "Just sideload the APK" | "Download and install the file" |
| **Don't be vague** | "Let me know what you think" | "Fill out this form with your feedback" |
| **Don't ignore feedback** | Tester reports bug, you don't respond | Always acknowledge and update status |
| **Don't make it feel like work** | "You MUST test these 20 scenarios" | "Try the core feature for 20 minutes" |
| **Don't send long emails** | 10 paragraphs of instructions | Keep it short, link to full guide |
| **Don't forget to close the loop** | Beta ends, no follow-up | Send wrap-up email with results |

---

## Best Practices

### Timing & Frequency

| Touchpoint | Timing | Purpose |
|------------|--------|---------|
| **Initial Invite** | Week -1 | Recruit testers |
| **Welcome Email** | Upon acceptance | Provide APK + guide |
| **Reminder 1** | Day 3 | Gentle nudge |
| **Reminder 2** | Day 7 | Final nudge |
| **Mid-Beta Check-in** | Week 1 | Collect interim feedback |
| **Thank You Email** | Upon feedback submission | Acknowledge contribution |
| **Issue Follow-up** | As needed | Update on reported bugs |
| **Wrap-up Email** | End of beta | Close the loop |

### Personalization Tips

- Use tester's first name (not full name or email)
- Reference their specific feedback if following up
- Adjust tone based on relationship (casual for friends, professional for colleagues)
- Mention shared context (e.g., "Remember you said X was confusing? I fixed it!")

### Response SLA

| Tester Action | Your Response Time | What to Do |
|---------------|-------------------|------------|
| Asks a question | < 24 hours | Answer directly or provide resource link |
| Reports a bug | < 48 hours | Acknowledge, confirm severity, provide timeline |
| Submits feedback | < 72 hours | Thank them, summarize key takeaways |
| No response after 7 days | 1 reminder | Gentle follow-up, offer to help |
| Asks to quit | Immediately | Thank them, remove from list |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Free Beta Tester Guide | `free-beta-tester-guide.md` | Comprehensive guide for testers |
| Beta Feedback Form | `beta-feedback-form.md` | Structured feedback template |
| Bug Report Template | `bug-report-template.md` | Standard bug report format |
| Free Beta Launch Checklist | `free-beta-launch-checklist.md` | Launch execution checklist |
| Feedback Triage Workflow | `feedback-triage.md` | How to process feedback |
| Launch Communications | `launch-communications.md` | Broader communication strategy |
| Beta Tester Tracker | `beta-tester-tracker.md` | Track tester status and feedback |
| Release Documentation Hub | `index.md` | All release docs entry point |

---

## Template Usage Notes

- **Copy entire template** and fill in placeholders
- **Customize tone** based on audience segment
- **Translate to other languages** if testing internationally
- **A/B test subject lines** for better open rates
- **Track responses** in Beta Tester Tracker
- **Iterate templates** based on what works

---

**Last Updated**: 2025-12-24
**Maintained By**: Product/PM Team
**Review Cadence**: After each beta cycle
