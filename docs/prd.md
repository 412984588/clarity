# Clarity - Product Requirements Document (PRD)

> **Version**: 1.0
> **Last Updated**: 2025-12-21
> **Status**: Draft
> **Author**: Product Team

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Target Users & Scenarios](#2-target-users--scenarios)
3. [Core User Journey - Solve 5 Steps](#3-core-user-journey---solve-5-steps)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Subscription & Permission Matrix](#6-subscription--permission-matrix)
7. [Risk & Compliance](#7-risk--compliance)
8. [Analytics & Key Metrics](#8-analytics--key-metrics)
9. [Milestones](#9-milestones)
10. [Appendix](#appendix)

---

## 1. Product Overview

### 1.1 Background & Vision

In an era of information overload and decision fatigue, people struggle to find clarity when facing life's challenges—whether career crossroads, relationship conflicts, or major life decisions. Traditional solutions (therapy, coaching, advice columns) are often expensive, inaccessible, or lack actionable guidance.

**Clarity** is an AI-powered problem-solving and decision assistant that helps users:
- Identify the **root cause** of their problems
- Gain new **perspectives** through cognitive reframing
- Receive **actionable, step-by-step solutions**

Unlike generic chatbots, Clarity follows a structured 5-step methodology (Solve) that guides users from emotional acknowledgment to committed action.

### 1.2 Product Goals

| Goal | Description |
|------|-------------|
| **G1** | Help users find clarity on complex personal and professional problems |
| **G2** | Provide actionable solutions, not just generic advice |
| **G3** | Create an emotionally intelligent experience (recognize and adapt to user emotions) |
| **G4** | Build a sustainable SaaS business with tiered subscriptions |
| **G5** | Ensure user privacy with local-first data philosophy |

### 1.3 Success Metrics (North Star)

| Metric | Target | Timeframe |
|--------|--------|-----------|
| **Problem Resolution Rate** | 70% of Solve sessions reach Commit step | V1 Launch |
| **Weekly Active Users (WAU)** | 10,000 | Month 3 |
| **Paid Conversion Rate** | 5% Free → Standard | Month 3 |
| **D7 Retention** | 40% | V1 Launch |
| **NPS Score** | > 50 | Month 6 |

---

## 2. Target Users & Scenarios

### 2.1 User Personas

#### Persona 1: Career Climber (Alex, 28)

| Attribute | Description |
|-----------|-------------|
| **Background** | Mid-level professional, 3-5 years experience |
| **Pain Points** | Career stagnation, difficult bosses, work-life balance |
| **Goals** | Get promoted, negotiate salary, switch jobs |
| **Tech Savvy** | High (uses ChatGPT, Notion, etc.) |
| **Willingness to Pay** | Moderate ($15-30/month for valuable tools) |

#### Persona 2: Relationship Navigator (Maria, 35)

| Attribute | Description |
|-----------|-------------|
| **Background** | Working professional, in long-term relationship or recently single |
| **Pain Points** | Communication issues, family conflicts, dating anxiety |
| **Goals** | Improve relationships, set boundaries, find balance |
| **Tech Savvy** | Medium |
| **Willingness to Pay** | Low-Moderate (values emotional support) |

#### Persona 3: Life Decision Maker (James, 42)

| Attribute | Description |
|-----------|-------------|
| **Background** | Established career, family responsibilities |
| **Pain Points** | Major life decisions (buying house, relocating, investing) |
| **Goals** | Make informed decisions, reduce regret anxiety |
| **Tech Savvy** | Medium |
| **Willingness to Pay** | High (values professional advice) |

### 2.2 Use Scenarios

| Scenario | Example | User Emotion | Expected Outcome |
|----------|---------|--------------|------------------|
| **Workplace** | "My boss takes credit for my work" | Frustrated | Concrete strategy to address the situation |
| **Relationship** | "Should I break up with my partner?" | Confused | Clarity on values, pros/cons analysis |
| **Major Decision** | "Should I accept a job in another city?" | Anxious | Decision framework, first action step |
| **Daily Dilemma** | "I can't decide between two job offers" | Overwhelmed | Side-by-side comparison, recommendation |

### 2.3 User Pain Points

1. **Lack of objectivity** - Friends/family give biased advice
2. **Analysis paralysis** - Too many factors to consider
3. **Emotional overwhelm** - Can't think clearly when stressed
4. **No actionable steps** - Know the problem but not the solution
5. **Privacy concerns** - Don't want to share sensitive issues with others

---

## 3. Core User Journey - Solve 5 Steps

### 3.1 Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOLVE FRAMEWORK                          │
├─────────┬─────────┬─────────┬─────────┬─────────────────────────┤
│ RECEIVE │ CLARIFY │ REFRAME │ OPTIONS │        COMMIT           │
│ 接纳    │ 澄清    │ 重构    │ 方案    │        承诺             │
├─────────┼─────────┼─────────┼─────────┼─────────────────────────┤
│ User    │ AI asks │ AI      │ AI      │ User commits to action  │
│ shares  │ 5W1H    │ offers  │ presents│ AI breaks down first    │
│ problem │ deep    │ new     │ 2-3     │ step                    │
│         │ dive    │ angles  │ options │                         │
├─────────┼─────────┼─────────┼─────────┼─────────────────────────┤
│ Emotion │ Root    │ Mindset │ Action  │ Commitment              │
│ Support │ Cause   │ Shift   │ Plan    │ Tracking                │
└─────────┴─────────┴─────────┴─────────┴─────────────────────────┘
```

### 3.2 Step-by-Step Details

#### Step 1: Receive (接纳)

| Aspect | Description |
|--------|-------------|
| **User Action** | Shares problem in natural language |
| **AI Behavior** | Emotion detection + empathetic response |
| **UI Change** | Background gradient shifts based on detected emotion |
| **Duration** | 1-2 exchanges |
| **Goal** | User feels heard and understood |

**Example Dialog:**
```
User: "I'm so frustrated. My colleague keeps undermining me in meetings
       and my manager doesn't seem to notice or care."

AI: "That sounds incredibly frustrating. Being undermined by a colleague
    while feeling unseen by your manager is exhausting. Let me help you
    work through this. Can you tell me more about what happened?"
```

#### Step 2: Clarify (澄清)

| Aspect | Description |
|--------|-------------|
| **User Action** | Answers clarifying questions |
| **AI Behavior** | Uses 5W1H framework to uncover root cause |
| **UI Change** | Progress indicator shows "Clarifying" |
| **Duration** | 3-5 exchanges |
| **Goal** | Identify the real problem beneath the surface |

**Clarifying Questions Framework (5W1H):**
- **What** - What specifically happened?
- **Who** - Who is involved?
- **When** - When did this start?
- **Where** - In what context?
- **Why** - Why do you think this is happening?
- **How** - How has this affected you?

#### Step 3: Reframe (重构)

| Aspect | Description |
|--------|-------------|
| **User Action** | Considers new perspectives |
| **AI Behavior** | Applies cognitive reframing techniques |
| **UI Change** | Visual cue indicating "new perspective" |
| **Duration** | 1-2 exchanges |
| **Goal** | User sees the situation differently |

**Reframing Techniques:**
1. **Devil's Advocate** - Consider the other person's perspective
2. **Zoom Out** - What will this matter in 5 years?
3. **Best Friend Test** - What would you tell a friend in this situation?
4. **Control Circle** - What can you actually control?
5. **Growth Lens** - What can you learn from this?

#### Step 4: Options (方案)

| Aspect | Description |
|--------|-------------|
| **User Action** | Reviews options presented |
| **AI Behavior** | Presents 2-3 actionable options with pros/cons |
| **UI Change** | Card-based option display |
| **Duration** | 1-2 exchanges |
| **Goal** | User has clear paths forward |

**Option Presentation Format:**
```
┌─────────────────────────────────────────────────────────────────┐
│ OPTION A: Direct Conversation                                   │
├─────────────────────────────────────────────────────────────────┤
│ Actions:                                                        │
│ 1. Schedule 1:1 with colleague                                  │
│ 2. Use "I" statements to express impact                         │
│ 3. Propose collaboration framework                              │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Pros: Direct, builds relationship, quick resolution          │
│ ❌ Cons: Uncomfortable, requires vulnerability                  │
│ ⏱️ Effort: Medium                                               │
│ 📈 Success Rate: 65%                                            │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 5: Commit (承诺)

| Aspect | Description |
|--------|-------------|
| **User Action** | Selects an option and commits to action |
| **AI Behavior** | Breaks down first step, offers reminder |
| **UI Change** | Action card with first step highlighted |
| **Duration** | 1 exchange |
| **Goal** | User has a concrete next action |

**Commitment Format:**
```
You've chosen Option A: Direct Conversation

📌 Your FIRST STEP (do within 48 hours):
"Send a calendar invite to [Colleague] for a 15-minute
 coffee chat with subject 'Quick sync'"

🔔 Want me to remind you about this?
□ Tomorrow at 9 AM
□ In 2 days
□ No reminder needed
```

### 3.3 Emotion Detection & UI Color System

| Emotion State | Color Gradient | HSL Values | Trigger Words/Patterns |
|---------------|----------------|------------|------------------------|
| **Anxious/Angry** | Orange-Red | `hsl(15, 85%, 55%)` → `hsl(0, 80%, 50%)` | frustrated, angry, can't stand, furious |
| **Sad/Depressed** | Blue-Purple | `hsl(220, 70%, 55%)` → `hsl(270, 60%, 45%)` | sad, hopeless, empty, lost |
| **Calm/Positive** | Green | `hsl(120, 40%, 50%)` → `hsl(150, 45%, 55%)` | good, better, hopeful, thank you |
| **Confused/Torn** | Yellow-Orange | `hsl(45, 80%, 55%)` → `hsl(30, 75%, 50%)` | don't know, confused, not sure, torn |
| **Neutral** | Gray-Blue | `hsl(210, 20%, 60%)` → `hsl(200, 25%, 55%)` | (default) |

**Implementation Notes:**
- Color transition should be subtle and gradual (300ms ease)
- Only applies to background, not text (accessibility)
- User can disable in settings

---

## 4. Functional Requirements

### 4.1 MVP Features

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| **FR1** | User Authentication | Google, Apple, Email sign-in (no guest mode) | P0 |
| **FR2** | Chat Interface | ChatGPT-like conversational UI | P0 |
| **FR3** | Solve 5-Step Flow | Guided problem-solving framework | P0 |
| **FR4** | Emotion Detection | Basic sentiment analysis (positive/negative/neutral) | P1 |
| **FR5** | Subscription System | Free tier with 10 sessions | P0 |
| **FR6** | Payment Integration | Stripe for US, compatible with Spain | P0 |
| **FR7** | Session Counter | Track and enforce usage limits | P0 |
| **FR8** | Basic i18n | English + Spanish UI | P1 |

### 4.2 V1 Features

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| **FR9** | Full Emotion Spectrum | 5 emotion states with color gradients | P1 |
| **FR10** | Conversation History | View past sessions (30 days for Standard) | P1 |
| **FR11** | Full i18n | English + Spanish + Chinese | P1 |
| **FR12** | Push Notifications | Action reminders (Commit step) | P2 |
| **FR13** | Device Management | View/revoke active sessions | P1 |
| **FR14** | Usage Dashboard | Personal analytics for users | P2 |

### 4.3 V2 Features

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| **FR15** | Organization Tier | Team management, seat-based billing | P1 |
| **FR16** | Deep Analysis Mode | Extended Clarify phase with AI prompts | P1 |
| **FR17** | Export Function | Download conversation as PDF/markdown | P2 |
| **FR18** | Priority Queue | Pro users get faster response times | P2 |
| **FR19** | Team Analytics | Usage reports for Org admins | P1 |
| **FR20** | SSO Integration | SAML/OIDC for enterprises | P2 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| **NFR1** | First response time | < 2 seconds |
| **NFR2** | Subsequent response time | < 3 seconds |
| **NFR3** | Page load time (LCP) | < 2.5 seconds |
| **NFR4** | API availability | 99.9% uptime |
| **NFR5** | Concurrent users | Support 10,000 concurrent |

### 5.2 Security

| ID | Requirement | Implementation |
|----|-------------|----------------|
| **NFR6** | Data encryption at rest | AES-256 |
| **NFR7** | Data encryption in transit | TLS 1.3 |
| **NFR8** | Authentication tokens | JWT with 24h expiry, refresh tokens |
| **NFR9** | OWASP Top 10 | Address all vulnerabilities |
| **NFR10** | Rate limiting | 60 requests/minute per user |

### 5.3 Privacy

| ID | Requirement | Implementation |
|----|-------------|----------------|
| **NFR11** | Default anonymization | PII stripped before AI processing |
| **NFR12** | Local-first storage | Conversation cache in browser (IndexedDB) |
| **NFR13** | Minimal server retention | Only store: user ID, usage count, subscription status |
| **NFR14** | Right to deletion | Full data deletion within 72 hours |
| **NFR15** | Data backup | 24-hour server backup (essential data only) |

**"Essential Data" Definition:**
- User account info (email, subscription status)
- Usage metrics (session count, last active)
- Billing records (Stripe customer ID, invoice history)

**NOT backed up:**
- Conversation content (stays local or deleted)
- Personal details shared in sessions

### 5.4 Anti-Abuse

| ID | Measure | Trigger | Action |
|----|---------|---------|--------|
| **NFR16** | Device fingerprinting | New device login | Verification email |
| **NFR17** | Concurrent session limit | > 2 active sessions | Force logout oldest |
| **NFR18** | Rate limiting | > 60 req/min | Temporary block (5 min) |
| **NFR19** | Velocity detection | 5 sessions in 1 hour | CAPTCHA challenge |
| **NFR20** | Sharing detection | Same account, different IPs, < 1 hour apart | Warning → account review |

### 5.5 Cost Control

| ID | Requirement | Implementation |
|----|-------------|----------------|
| **NFR21** | AI API budget | Cap at $0.05/session for GPT-4 tier |
| **NFR22** | Prompt optimization | Use efficient prompts, cache common responses |
| **NFR23** | Infrastructure | Serverless (Cloudflare Workers) for auto-scaling |
| **NFR24** | CDN | Static assets on edge (Cloudflare) |

---

## 6. Subscription & Permission Matrix

### 6.1 Pricing Table

| Tier | Price | Session Limit | Billing |
|------|-------|---------------|---------|
| **Free** | $0 | 10 sessions (lifetime) | One-time grant |
| **Standard** | $14.99/month | 100 sessions/month | Monthly, annual option (-20%) |
| **Pro** | $29.99/month | Unlimited | Monthly, annual option (-20%) |
| **Organization** | $19.99/seat/month | Unlimited per seat | Monthly, min 5 seats |

**Overage (Standard only):** $0.20 per session beyond 100

### 6.2 Feature Permission Matrix

| Feature | Free | Standard | Pro | Org |
|---------|:----:|:--------:|:---:|:---:|
| Solve 5-Step Framework | ✅ | ✅ | ✅ | ✅ |
| Emotion-Based UI Colors | ✅ | ✅ | ✅ | ✅ |
| Basic Languages (EN/ES) | ✅ | ✅ | ✅ | ✅ |
| Conversation History | ❌ | 30 days | Forever | Forever |
| Deep Analysis Mode | ❌ | ❌ | ✅ | ✅ |
| Export Conversations | ❌ | ❌ | ✅ | ✅ |
| Priority Response Queue | ❌ | ❌ | ✅ | ✅ |
| Action Reminders | ❌ | ✅ | ✅ | ✅ |
| Multi-device Sync | ❌ | ✅ | ✅ | ✅ |
| Team Management | ❌ | ❌ | ❌ | ✅ |
| Usage Reports (Admin) | ❌ | ❌ | ❌ | ✅ |
| SSO Integration | ❌ | ❌ | ❌ | ✅ |
| VIP Support | ❌ | ❌ | ✅ | ✅ |

### 6.3 Upgrade Prompts

| Trigger | Message |
|---------|---------|
| Free user reaches 8/10 sessions | "You've used 8 of 10 free sessions. Upgrade to Standard for unlimited problem-solving." |
| Free user hits limit | "You've used all free sessions. Upgrade now to continue your journey." |
| Standard user at 90% quota | "You've used 90 sessions this month. Upgrade to Pro for unlimited access." |
| Standard user uses Deep Analysis feature (locked) | "Deep Analysis is a Pro feature. Upgrade to unlock deeper insights." |

---

## 7. Risk & Compliance

### 7.1 United States Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **CCPA** (California) | Right to know, delete, opt-out | Privacy dashboard, deletion API, no data selling |
| **COPPA** | Parental consent for < 13 | Age gate on signup, no under-13 accounts |
| **CAN-SPAM** | Email opt-out | Unsubscribe link in all marketing emails |

### 7.2 Spain / EU Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **GDPR** | Consent, data minimization, portability | Cookie banner, minimal data collection, export API |
| **GDPR** | DPO (if large scale processing) | Monitor threshold, prepare DPO appointment |
| **GDPR** | Cross-border transfers | EU data stays in EU (Frankfurt region) |
| **LSSI-CE** (Spain) | Commercial communication rules | Clear sender, opt-out |

### 7.3 Payment Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **PCI-DSS** | Secure card handling | Delegate to Stripe (Level 1 PCI) |
| **SCA** (EU) | Strong Customer Authentication | Stripe 3D Secure for EU cards |
| **PSD2** | Payment security | Stripe compliance |

### 7.4 AI-Specific Risks

| Risk | Mitigation |
|------|------------|
| **Harmful advice** | Disclaimer: "This is not professional therapy or legal advice" |
| **User crisis (self-harm)** | Crisis detection → surface hotline numbers |
| **Data leakage in prompts** | PII stripping before sending to AI |
| **Bias in responses** | Regular bias audits, diverse training data |

---

## 8. Analytics & Key Metrics

### 8.1 North Star Metric

**Problem Resolution Rate (PRR)**
= Sessions reaching Commit step / Total sessions started

**Target:** 70%

### 8.2 Activation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Signup-to-First-Session** | % of signups that complete 1 session | 60% |
| **Time-to-First-Value** | Time from signup to completing Commit step | < 10 min |
| **First Session Completion** | % of first sessions that reach Commit | 50% |

### 8.3 Retention Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **D1 Retention** | Users returning day after signup | 30% |
| **D7 Retention** | Users returning within 7 days | 40% |
| **D30 Retention** | Users returning within 30 days | 25% |
| **WAU/MAU Ratio** | Weekly to monthly active users | 40% |

### 8.4 Revenue Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Free → Paid Conversion** | % of free users upgrading | 5% |
| **Standard → Pro Upgrade** | % of Standard upgrading to Pro | 15% |
| **Monthly Churn (Standard)** | % canceling Standard | < 8% |
| **Monthly Churn (Pro)** | % canceling Pro | < 5% |
| **LTV:CAC Ratio** | Customer lifetime value / Acquisition cost | > 3:1 |

### 8.5 Event Tracking Specification

| Event Name | Trigger | Properties |
|------------|---------|------------|
| `session_started` | User begins new Solve session | `session_id`, `user_tier` |
| `step_completed` | User completes a Solve step | `step_name`, `duration_sec` |
| `session_completed` | User reaches Commit step | `session_id`, `total_duration` |
| `session_abandoned` | User leaves mid-session | `last_step`, `duration_sec` |
| `emotion_detected` | Emotion changes | `emotion_type`, `confidence` |
| `option_selected` | User picks an option in Step 4 | `option_index` |
| `reminder_set` | User enables reminder in Step 5 | `reminder_time` |
| `upgrade_prompt_shown` | Upgrade modal displayed | `trigger_reason`, `user_tier` |
| `upgrade_completed` | User upgrades subscription | `from_tier`, `to_tier` |
| `payment_failed` | Payment attempt fails | `error_code` |

---

## 9. Milestones

### Phase 1: Foundation (Week 1-2)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W1 | Project setup (repo, CI/CD, environments) | Dev |
| W1 | Tech stack finalization | Architect |
| W1 | Database schema design | Backend |
| W2 | API skeleton (auth endpoints) | Backend |
| W2 | UI component library setup | Frontend |
| W2 | i18n infrastructure | Frontend |

### Phase 2: Authentication + Chat (Week 3-4)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W3 | Google OAuth integration | Backend |
| W3 | Apple Sign-in integration | Backend |
| W3 | Email/password auth + email verification | Backend |
| W3 | Auth UI (login, signup, password reset) | Frontend |
| W4 | Chat interface (message list, input) | Frontend |
| W4 | WebSocket/SSE for real-time streaming | Backend |
| W4 | Session management (create, load, list) | Full-stack |

### Phase 3: Solve Flow (Week 5-6)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W5 | AI integration (OpenAI/Claude) | Backend |
| W5 | Solve prompt engineering (5 steps) | AI/Product |
| W5 | Emotion detection service | AI |
| W6 | Step progression logic | Backend |
| W6 | Option card UI component | Frontend |
| W6 | Commit step with reminder scheduling | Full-stack |
| W6 | UI color gradient system | Frontend |

### Phase 4: Subscription + Payment (Week 7-8)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W7 | Stripe integration (US) | Backend |
| W7 | Subscription tiers implementation | Backend |
| W7 | Session counter + limit enforcement | Backend |
| W8 | Pricing page UI | Frontend |
| W8 | Upgrade flow (in-app) | Full-stack |
| W8 | Payment webhook handling | Backend |
| W8 | Invoice + receipt emails | Backend |

### Phase 5: i18n + Anti-Abuse (Week 9-10)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W9 | Full Spanish translation | Content |
| W9 | Language switcher UI | Frontend |
| W9 | Locale-aware formatting (dates, currency) | Full-stack |
| W10 | Device fingerprinting | Backend |
| W10 | Rate limiting implementation | Backend |
| W10 | Concurrent session detection | Backend |
| W10 | Abuse monitoring dashboard | Backend |

### Phase 6: Testing + Launch (Week 11-12)

| Week | Deliverable | Owner |
|------|-------------|-------|
| W11 | End-to-end testing | QA |
| W11 | Performance testing (load test) | DevOps |
| W11 | Security audit | Security |
| W11 | GDPR/CCPA compliance review | Legal |
| W12 | Staging environment validation | All |
| W12 | Production deployment | DevOps |
| W12 | Launch monitoring setup | DevOps |
| W12 | Go-live (soft launch) | All |

---

## Appendix

### A. Emotion-Color Mapping Reference

```css
/* Anxious/Angry */
--emotion-anxious: linear-gradient(135deg, hsl(15, 85%, 55%) 0%, hsl(0, 80%, 50%) 100%);

/* Sad/Depressed */
--emotion-sad: linear-gradient(135deg, hsl(220, 70%, 55%) 0%, hsl(270, 60%, 45%) 100%);

/* Calm/Positive */
--emotion-calm: linear-gradient(135deg, hsl(120, 40%, 50%) 0%, hsl(150, 45%, 55%) 100%);

/* Confused/Torn */
--emotion-confused: linear-gradient(135deg, hsl(45, 80%, 55%) 0%, hsl(30, 75%, 50%) 100%);

/* Neutral (default) */
--emotion-neutral: linear-gradient(135deg, hsl(210, 20%, 60%) 0%, hsl(200, 25%, 55%) 100%);
```

### B. API Rate Limits

| Tier | Requests/Minute | Sessions/Day | Concurrent |
|------|-----------------|--------------|------------|
| Free | 30 | 3 | 1 |
| Standard | 60 | 10 | 2 |
| Pro | 120 | Unlimited | 3 |
| Org | 200/seat | Unlimited | 5/seat |

### C. Crisis Detection Keywords

When detected, surface appropriate hotline:

**US:**
- National Suicide Prevention: 988
- Crisis Text Line: Text HOME to 741741

**Spain:**
- Teléfono de la Esperanza: 717 003 717

**Trigger Phrases:**
- "want to die", "kill myself", "end it all", "no point in living"
- "quiero morir", "suicidarme", "acabar con todo"

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-21 | 1.0 | Initial PRD draft | Product Team |

---

*This document is maintained by the Product Team. For questions or suggestions, contact product@clarity.app*
