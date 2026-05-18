# Quest English — Interview Quest Pack MVP PRD

| 字段 | 内容 |
|------|------|
| **文档版本** | v1.0 |
| **状态** | Draft — 待 Discovery 验证 |
| **负责人** | Product |
| **工程仓库** | `english-interview-platform` |
| **关联文档** | [product-strategy-global-english-app.md](./product-strategy-global-english-app.md)、[prd-mvp-feature-list.md](./prd-mvp-feature-list.md)、[prd-mvp-engineering-epics.md](./prd-mvp-engineering-epics.md)、[techspec-us004-voice-asr.md](./techspec-us004-voice-asr.md)、[adr-001-service-boundaries.md](./adr-001-service-boundaries.md) |
| **方法来源** | `E:\产品经理\Product-Manager-Skills` — `prd-development`、`problem-statement`、`positioning-statement`、`epic-hypothesis`、`user-story` |
| **目标发布** | MVP 内测（T+12 周，以 Discovery 通过为前提） |

---

## 1. Executive Summary

我们为 **18–30 岁、需要在英文面试/职场关键场景中开口的非母语求职者**，打造一款 **App-first 的「情境副本」英语口语训练产品（Quest English）**。MVP 以 **「Interview Quest Pack」**（自我介绍 + Behavioral 面试）为首个副本包，通过 **3–5 分钟语音回合 + 结构化即时反馈 + 可分享的进步护照章**，解决用户在 Duolingo 等工具上「练了很多却不敢真开口、上场仍哑火」的核心痛点。

本阶段不追求「全球多邻国式泛英语学习」，而验证：**游戏化若绑定真实场景开口与可感知进步，能否带来 ≥40% 的 Session 完成率与 ≥25% 的 7 日回访率**。技术上复用已打通的 `mobile → api-gateway → session-service → PostgreSQL` 主链路，在现有 `session / turn / stage / scores` 模型上扩展副本元数据与 Passport 快照。

---

## 2. Problem Statement

### 2.1 Problem Framing Narrative

- **I am：** 准备外企/海外岗位面试的非母语求职者（本科–硕士，有一定阅读基础，口语不自信）。
- **Trying to：** 在真实面试中流畅完成 Self-intro 与 Behavioral 问题，让面试官听懂我的经历与动机。
- **But：** 我缺乏高压下的连续口语输出练习；现有 App 多为点选/拼句，练完仍不敢开口；真人外教贵且难约。
- **Because：** 练习与真实场景脱节；反馈偏分数或语法点，而非「下一轮怎么说更好」；缺少可验证的进步证明。
- **Which makes me feel：** 焦虑、丢脸、担心「准备了白准备」。

### 2.2 谁有这个问题？

| 优先级 | 人群 | 场景 |
|--------|------|------|
| P0 | 求职型非母语用户 | 英文视频/现场面试前 2–8 周 |
| P1 | 在职转岗/晋升用户 | 英文 1:1、汇报、客户会议 |
| P2 | 留学申请用户 | Admission / 签证面谈（后续副本包） |

MVP **仅服务 P0**。

### 2.3 问题是什么？（可验证表述）

用户在「必须开口」的真实场景中 **无法组织 60–120 秒的连贯英文回答**，具体表现为：

1. 回答过短、缺例子（STAR 不完整）；
2. 紧张导致卡顿、回避细节；
3. 练过的模板无法应对追问。

### 2.4 为什么痛？（用户 + 业务）

| 维度 | 影响 |
|------|------|
| **用户** | 错失 offer；重复报班/外教仍无效；自我效能感下降 |
| **业务** | 口语细分赛道增长快于纯题库；Duolingo 开口弱项被竞品反复提及；AI 对话产品同质化下 **场景+结果** 仍是差异化窗口 |

### 2.5 证据（待 Discovery 补齐，当前为假设 + 市场二手）

| 类型 | 内容 | 状态 |
|------|------|------|
| 竞品评测 | Duolingo：Hearts 限次、开口不足（PolyChat/Univext 2026） | 二手 |
| 行业趋势 | 数字英语学习市场 CAGR ~12–15%；发音/口语增速更高 | 二手 |
| 用户访谈 | 「上次不得不讲英语却卡住」故事 ≥10 条 | **待办** |
| 原型测试 | 完成 1 次 Interview Quest Session 的比例 | **待办** |

**Discovery Gate（MVP 开工前）：** 完成 ≥10 次深度访谈，且 ≥6/10 明确表达「愿意每天练 3 分钟语音面试题」。

---

## 3. Target Users & Personas

### 3.1 Primary Persona：求职备面者 Lin

| 属性 | 描述 |
|------|------|
| 年龄 | 22–28 |
| 地区 | 中国/东南亚/拉美城市化用户（英语为第二语言） |
| 目标 | 4–8 周内拿到外企或远程岗 offer |
| 行为 | 用过 Duolingo/百词斩；买过或考虑过外教；面试前临时抱佛脚 |
| 痛点 | 知道要练口语，不知练什么、如何复盘 |
| 成功标准 | 「模拟面试后敢开口」+ 能说出 1 条具体改进点 |

### 3.2 Secondary Persona：在职晋升者 Alex（Out of MVP）

- 25–40 岁，需英文汇报；愿付费但时间碎片化——Phase 2「职场副本包」覆盖。

### 3.3 Jobs-to-be-Done

| 功能型 Job | 情感型 Job | 社会型 Job |
|-----------|-----------|-----------|
| 在面试中清晰介绍自己并回答 Behavioral 题 | 减少紧张、增强掌控感 | 在面试官面前显得专业、可信 |

**核心 Job 陈述（MVP）：**  
*When I have an English interview coming up, help me practice speaking out loud in realistic questions so I can improve one concrete thing each day and feel ready.*

---

## 4. Strategic Context

### 4.1 Positioning Statement

**Value Proposition**

- **For** 需要在英文面试中开口的非母语求职者  
- **that need** 在真实高压场景下练习连续口语、并获得可执行的改进建议  
- **Quest English**（工作名）  
- **is a** 情境副本式英语口语训练 App  
- **that** 让你在 3–5 分钟内完成一局「面试副本」、开口作答并获得结构化反馈与可分享的进步证明  

**Differentiation Statement**

- **Unlike** Duolingo 等以点选/识词为主、开口为辅的泛英语学习 App  
- **Quest English**  
- **provides** 以「面试情境副本」为单位的必做语音回合、无限次基础练习（MVP 不设 Hearts）、以及绑定结果感的 Passport 进步章  

### 4.2 业务目标（MVP 阶段 OKR 草案）

| Objective | Key Result | 目标值 |
|-----------|------------|--------|
| 验证楔子 PMF 信号 | Session 完成率（bootstrap → 提交 ≥1 turn → 查看 feedback） | ≥ 40% |
| 验证习惯雏形 | D7 回访率（完成 ≥2 次 Quest） | ≥ 25% |
| 验证结果感 | 反馈页「有帮助」占比（应用内 1-tap） | ≥ 60% |
| 控制成本 | 免费用户日均 AI 成本 | 待财务模型（见 Open Questions） |

### 4.3 市场机会（量级，非精确预测）

| 层级 | 估算逻辑 |
|------|---------|
| **TAM** | 全球数字英语学习 ~$140–260B（2025，多家机构） |
| **SAM** | 移动端、求职/职场口语动机用户（数亿） |
| **SOM（MVP）** | 首年聚焦英/中界面 + 面试副本，目标 **1–5 万** 周活开口用户验证 |

### 4.4 竞争格局（摘要）

| 竞品 | 强项 | 缺口（我方机会） |
|------|------|----------------|
| Duolingo | 习惯、品牌、DAU | 开口少、心数、结果难证明 |
| Speak / ELSA | AI 对话 / 发音 | 面试情境与 offer 结果链弱 |
| Cambly | 真人 | 贵、难每日坚持 |
| 本题仓库现状 | 工程主链路已通 | 缺语音输入、真实 LLM、副本运营 |

### 4.5 Why Now?

1. AI 口语反馈成本下降，单人每日 3 分钟闭环可算清账；  
2. Duolingo 2026 转向冲 DAU，深度「场景口语价值」仍留白；  
3. 本仓库已完成 `session-service` PostgreSQL 持久化与移动端五屏流程，**边际开发聚焦产品与 AI，而非从零基建**。

---

## 5. Solution Overview

### 5.1 产品定义（MVP）

**Quest English — Interview Quest Pack MVP** 是一款移动端 App，用户选择目标岗位类型 → 进入「面试副本」→ 完成 **1 局 3–5 分钟语音问答**（含 1 轮自答 + 结构化反馈）→ 查看分数与改进建议 → 获得 **Passport 章**（可分享）→ 驱动次日再练（个人 Streak）。

### 5.2 核心用户流程

```text
[Onboarding] 选择语言/UI + 目标（Job Interview） + 岗位方向（Product / General）
      ↓
[Quest Map]  Interview Quest Pack（解锁：Self-intro、Behavioral）
      ↓
[Quest Start] 展示本局目标、预计 3 min、面试官人设（文案）
      ↓
[Voice Round] 听题 → 录音作答（≥30s 建议）→ 提交
      ↓
[Feedback]  turn 级 summary + improvementTip；session 级 scores + stage
      ↓
[Passport]  本局章 + 历史；可选分享图
      ↓
[Home]      今日是否完成 + Streak + 推荐下一副本
```

### 5.3 MVP 功能清单

> **完整功能清单（42 项 + API 7 项 + P0 验收 Gate）见：** [prd-mvp-feature-list.md](./prd-mvp-feature-list.md)

下表为 **模块级摘要**（便于 PRD 速览）：

| 模块 | 功能点数 | P0 | 已实现（约） | 本版重点 |
|------|---------|-----|-------------|---------|
| A. 启动与引导 | 4 | 3 | 1 | Onboarding 与 role 合并 |
| B. 首页与导航 | 3 | 2 | 2 | 首页 Streak |
| C. Quest 副本 | 6 | 5 | 3 | Quest Map + Start 页 |
| D. 面试 Session | 5 | 4 | 4 | 展示当前题 |
| E. 语音与 ASR | 7 | 6 | 0 | **差异化核心** |
| F. 反馈与评分 | 6 | 5 | 3 | 五维 UI + 有用性评价 |
| G. Passport | 5 | 4 | 0 | 章 + 分享 |
| H. 习惯留存 | 3 | 1 | 0 | Streak |
| I. 系统质量 | 7 | 2 | 2 | 埋点、隐私 |

**原 F1–F10 映射：**

| 原 ID | 新功能 ID | 名称 |
|-------|-----------|------|
| F1 | A-02, A-03 | Onboarding / 岗位 |
| F2 | C-01~C-05 | Quest Map & Pack |
| F3 | D-01 | Session Bootstrap |
| F4 | E-01~E-06 | 语音作答 |
| F5 | F-01, F-02 | 结构化反馈 |
| F6 | F-03 | Scores 五维 |
| F7 | G-01~G-05 | Passport |
| F8 | H-01, H-02 | Streak |
| F9 | E-07, I-02 | 弱网/错误态 |
| F10 | I-03 | 埋点 |

### 5.4 游戏化原则（MVP 范围）

| 机制 | MVP | 原则 |
|------|-----|------|
| 每日主任务 | ✅ 1 局 Quest | 降低决策成本 |
| Hearts 限次 | ❌ 不做 | 开口不限次 |
| 排行榜 | ❌ 不做 | Phase 2 小队 |
| XP/语法树 | ❌ 不做 | 用 Passport 章替代 |
| 副本叙事 | ✅ 轻量文案 | 短剧感标题+考官一句话 |

### 5.5 与现有技术对齐

| 概念 | 当前实现 | MVP 演进 |
|------|---------|---------|
| 副本 Quest | `missionId` | 增加 `questPackId=interview` 元数据（配置或 CMS） |
| 回合 Turn | `POST /v1/mobile/sessions/{id}/turns` | `answer` 来自 ASR 文本 |
| 状态机 | `stage`, `currentQuestion` | 沿用 `behavioral` 三问集 |
| 分数 | `scores` JSON | 后续接 LLM rubric；MVP 可保留规则引擎 |
| 持久化 | PostgreSQL `interview_sessions` | 增加 `passport_snapshots` 表（新） |

---

## 6. Success Metrics

### 6.1 北极星指标（产品级）

**周有效开口分钟数（Weekly Speaking Minutes, WSM）**

- 定义：用户在一周内 **主动提交** 的面试副本作答总时长（秒 → 分）。
- MVP 目标：内测 cohort 周人均 WSM ≥ **8 分钟**（约 2–3 局）。

### 6.2 一级指标（MVP 优化目标）

| 指标 | 定义 | 基线 | MVP 目标 | 观测窗口 |
|------|------|------|---------|---------|
| **Session 完成率** | 创建 session 且提交 ≥1 个有效 turn 的用户 / 创建 session 用户 | 未知 | ≥ 40% | 上线后 30 天 |
| **D7 留存** | 第 7 天完成 ≥2 局 Quest 的用户 / 新用户 | 未知 | ≥ 25% | 上线后 30 天 |
| **反馈有用率** | 反馈页点击「有帮助」/ 查看反馈页 | 未知 | ≥ 60% | 每版本 |

### 6.3 二级指标

| 指标 | 用途 |
|------|------|
| 平均作答时长 | 是否真正开口（非空提交） |
| Bootstrap → 首次提交延迟 | 流程摩擦 |
| Passport 分享率 | 增长验证 |
| Streak 长度分布 | 习惯质量 vs 僵尸 streak |

### 6.4 Guardrail 指标

| 指标 | 阈值 |
|------|------|
| 崩溃率 | < 1% sessions |
| API P95 延迟（gateway） | < 800ms（不含 ASR/LLM） |
| 用户投诉「反馈无用」 | < 15% |
| 免费用户单日 AI 成本 | 不超过预设上限（见 Open Questions） |

### 6.5 埋点事件（最小集）

| 事件 | 属性 |
|------|------|
| `onboarding_complete` | `goal`, `roleId` |
| `quest_start` | `questPackId`, `missionId` |
| `session_bootstrap` | `sessionId` |
| `turn_submit` | `sessionId`, `durationSec`, `wordCount` |
| `feedback_view` | `sessionId`, `readiness` |
| `feedback_helpful` | `sessionId`, `helpful: bool` |
| `passport_stamp_earned` | `stampId`, `missionId` |
| `passport_share` | `channel` |

---

## 7. User Stories & Requirements

### 7.1 Epic Hypothesis

**If we** 提供「Interview Quest Pack」——每日 3–5 分钟必做语音面试副本 + 结构化反馈 + Passport 章  
**for** 准备英文面试的非母语求职者  
**Then we will** 提升其在真实面试前的口语信心与可执行改进点  
**because** 现有工具缺少高压场景下的连续输出练习与结果感绑定。

**Tiny Acts of Discovery**

1. 10 人访谈 + 纸质原型（Quest Map → 一题录音 → 反馈卡片）；  
2. Wizard-of-Oz：人工撰写反馈，验证「有用率」；  
3. 技术 spike：移动端录音 + ASR + 现有 `turns` API 端到端。

**Validation（8 周内测）**

- Session 完成率 ≥ 40%；  
- 反馈有用率 ≥ 60%；  
- ≥ 3/10 用户自愿 D7 回访。

---

### 7.2 Release 切片

| 切片 | 内容 | 目标周 |
|------|------|--------|
| **R0** | Discovery + ASR spike | W1–W4 |
| **R1** | 语音提交 + 反馈增强（规则引擎） | W5–W8 |
| **R2** | Passport 章 + Streak + 埋点 | W9–W10 |
| **R3** | 内测 + 迭代 | W11–W12 |

---

### 7.3 User Stories

#### US-001：Onboarding 设定目标与岗位

- **Summary：** 新用户完成目标与岗位选择

**Use Case**

- **As a** 求职备面者 Lin  
- **I want to** 在首次打开时选择「Job Interview」和岗位类型  
- **So that** 后续副本和题目与我的面试相关  

**Acceptance Criteria**

- **Scenario：** 首次启动完成引导  
- **Given：** 用户首次安装并打开 App  
- **And Given：** 未完成过 onboarding  
- **When：** 用户选择 `Job Interview` 与 `Product`（或 `General`）并点击 Continue  
- **Then：** 本地保存 `goal` 与 `roleId`；进入 Quest Map；触发 `onboarding_complete`  

---

#### US-002：浏览 Interview Quest Pack

- **Summary：** 在 Quest Map 查看可用副本

**Use Case**

- **As a** Lin  
- **I want to** 看到 Interview Pack 下的 Self-intro 与 Behavioral 副本  
- **So that** 我知道今天练什么  

**Acceptance Criteria**

- **Scenario：** 展示两个 mission 入口  
- **Given：** 用户已完成 onboarding  
- **When：** 用户进入 Quest Map  
- **Then：** 显示 `self_intro`、`behavioral` 卡片（标题、预估时长、完成状态）；点击任一进入 Quest Start  

---

#### US-003：创建面试 Session（Bootstrap）

- **Summary：** 开始一局副本并拿到 sessionId

**Use Case**

- **As a** Lin  
- **I want to** 开始一局面试练习  
- **So that** 系统记录我的问答与反馈  

**Acceptance Criteria**

- **Scenario：** 成功创建 session  
- **Given：** 用户选定 `missionId`（如 `behavioral`）  
- **And Given：** `api-gateway` 与 `session-service` 可用  
- **When：** 客户端 `POST /v1/mobile/session/bootstrap`，body `{ roleId, missionId }`  
- **Then：** 返回 `sessionId`、`stage`、`currentQuestion`、seed `turns`（若已有）；进入 Voice Round；触发 `session_bootstrap`  

**API（已实现）**

```http
POST /v1/mobile/session/bootstrap
Content-Type: application/json

{ "roleId": "product", "missionId": "behavioral" }
```

---

#### US-004：语音录制并提交回答

- **Summary：** 用户录音作答并提交为 turn

**Use Case**

- **As a** Lin  
- **I want to** 用语音回答当前面试问题  
- **So that** 练习真实开口而不是打字  

**Acceptance Criteria**

- **Scenario：** 提交有效语音 turn  
- **Given：** 用户处于 Voice Round，显示 `currentQuestion`  
- **And Given：** 设备麦克风权限已授予  
- **When：** 用户录音 ≥10 秒并点击 Submit  
- **Then：** 音频经 ASR 转为文本；`POST /v1/mobile/sessions/{sessionId}/turns` body `{ answer }`；进入 Loading；成功后跳转 Feedback；触发 `turn_submit`  

**约束**

- 录音上限 120 秒；空文本拒绝提交并提示重录。  
- 弱网：最多自动重试 2 次，失败展示错误页与重试按钮。

**API（已实现）**

```http
POST /v1/mobile/sessions/{sessionId}/turns
Content-Type: application/json

{ "answer": "<ASR transcript text>" }
```

---

#### US-005：查看结构化反馈与分数

- **Summary：** 反馈页展示 turn 与 session 级结果

**Use Case**

- **As a** Lin  
- **I want to** 看到本题点评和整体分数  
- **So that** 知道下一轮如何改进  

**Acceptance Criteria**

- **Scenario：** 加载 session 详情  
- **Given：** 用户刚提交 turn 或从 History 进入  
- **When：** 客户端 `GET /v1/mobile/sessions/{sessionId}`  
- **Then：** 展示 `turns[].feedback.summary`、`improvementTip`；展示 `scores` 五维与 `readiness`；展示 `stage` 与下一题提示（若未结束）；提供「有帮助/无帮助」；触发 `feedback_view`  

---

#### US-006：获得 Passport 章

- **Summary：** 完成一局后获得可收集的进步章

**Use Case**

- **As a** Lin  
- **I want to** 在完成一局后获得一枚护照章  
- **So that** 看见进步并愿意分享  

**Acceptance Criteria**

- **Scenario：** 首次完成某 mission 局后发章  
- **Given：** 用户本次 session 已提交 ≥1 有效 turn  
- **When：** Feedback 页加载完成  
- **Then：** 展示本章图标（mission 名 + 日期 + readiness）；写入 `passport_snapshots`；用户可进入 Passport 列表；触发 `passport_stamp_earned`  

**数据（新增，工程待设计）**

- `passport_snapshots(id, user_id, session_id, mission_id, readiness, earned_at, share_payload_json)`

---

#### US-007：分享 Passport 章

- **Summary：** 生成分享图并调起系统分享

**Use Case**

- **As a** Lin  
- **I want to** 分享我的进步章到社交媒体  
- **So that** 记录动力并邀请朋友  

**Acceptance Criteria**

- **Scenario：** 分享成功调起系统面板  
- **Given：** 用户在某章详情页  
- **When：** 用户点击 Share  
- **Then：** 生成含 mission、readiness、产品名的图片；调起 OS share sheet；触发 `passport_share`  

---

#### US-008：个人 Streak

- **Summary：** 每日完成一局维持连续天数

**Use Case**

- **As a** Lin  
- **I want to** 看到连续练习天数  
- **So that** 有动力明天再来  

**Acceptance Criteria**

- **Scenario：** 完成当日首局增加 streak  
- **Given：** 用户今日尚未完成 Quest  
- **When：** 用户完成任意 mission 一局（有效 turn）  
- **Then：** `streakCount` +1；首页展示；跨日未练则归零（MVP 无护盾）  

---

#### US-009：错误与空状态

- **Summary：** 网络与服务失败可恢复

**Acceptance Criteria**

- Bootstrap/turns/detail 失败展示明确文案 + 重试；  
- 麦克风拒绝时引导去系统设置；  
- 无历史 Passport 时展示 Empty 态与 CTA「开始第一局」。

---

### 7.4 非功能需求（NFR）

| 类别 | 要求 |
|------|------|
| **性能** | 反馈页加载 < 2s（不含 ASR）；ASR P95 < 5s（地区待定） |
| **可用性** | 核心流程 3 步内进入录音（Map → Start → Record） |
| **安全** | 语音数据加密传输；隐私政策说明存储期限 |
| **国际化** | MVP：英文 UI + 中文辅助；题目英文 |
| **可访问性** | 核心按钮具备 accessibilityLabel（Expo） |
| **合规** | 13 岁以下不服务；GDPR 删除请求路径（可 Phase 2） |

### 7.5 数据模型（Session 域，延续现有）

```json
{
  "sessionId": "sess_xxx",
  "status": "in_progress",
  "stage": "deep_dive | closing",
  "currentQuestion": "string",
  "roleId": "product",
  "missionId": "behavioral",
  "turns": [{
    "id": "turn_xxx",
    "speaker": "candidate",
    "createdAt": "ISO8601",
    "question": "string",
    "answer": "string",
    "feedback": {
      "summary": "string",
      "improvementTip": "string"
    }
  }],
  "scores": {
    "clarity": 0,
    "structure": 0,
    "confidence": 0,
    "relevance": 0,
    "readiness": 0
  }
}
```

---

## 8. Out of Scope

以下明确 **不在 MVP** 范围内：

| 排除项 | 原因 |
|--------|------|
| 泛语法/单词/阅读课程 | 战略聚焦面试楔子 |
| Hearts / 体力值 | 与差异化「开口不限次」冲突 |
| 小队共 Streak / 公会 | Phase 2 |
| 真人外教市集 | 成本高、非 MVP |
| 多语言学习（西/法/日） | 仅英语 |
| 完整 LLM 考官自由对话 | MVP 用固定题集 + 结构化反馈；Max 层后续 |
| 订阅支付 | Phase 3；MVP 全免费内测 |
| Android 以外平台优先 | Expo 可扩，但测试资源优先 iOS/TestFlight |
| 企业 B2B 管理台 | Phase 3 |
| 实时 OpenAI Realtime 双向语音 | 成本高；先用 ASR + 文本反馈 |

**Future consideration**

- 留学/旅行副本包；口音选择；AI 深度复盘（Max）；小队 Boss 战。

---

## 9. Dependencies & Risks

### 9.1 依赖

| 依赖 | 负责 | 说明 |
|------|------|------|
| `api-gateway` / `session-service` | 工程 | 已通；需稳定 PostgreSQL smoke |
| 移动端录音 + ASR | 工程 | 第三方或云 ASR（待选型） |
| LLM 反馈（可选） | 工程/AI | MVP 可规则引擎；R1.5 接 LLM |
| 分享图生成 | 移动 | 本地 canvas / 模板 |
| 用户身份 | 工程 | MVP 可用匿名 `deviceId`；Passport 需持久用户键 |
| 隐私政策 / ToS | 法务 | 内测前必备 |

### 9.2 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| ASR 质量差导致反馈失真 | 高 | 允许用户编辑转写；低置信度提示重录 |
| 规则反馈显得「假」 | 高 | Discovery 测有用率；快速接 LLM |
| 与 Duolingo 正面竞争获客 | 高 | 定位面试细分；内容 SEO/短视频副本 |
| 免费 AI 成本失控 | 中 | 每日局数软上限；深度复盘付费墙 |
| Streak 僵尸化 | 中 | 北极星用 WSM 而非 DAU |
| 范围蔓延（加课程/社交） | 中 | 本 PRD Out of Scope 锁边界 |

**Anti-pattern 显式标注（prd-development Checkpoint）：**  
避免「先堆功能再验证」——若 W4 结束访谈显示用户不愿开口，则 **停止 R1**，不继续做 Passport/Streak。

---

## 10. Open Questions

| # | 问题 | 决策人 | 截止 |
|---|------|--------|------|
| OQ-1 | ASR 选型：设备端 vs 云端？ | Eng | R0 |
| OQ-2 | MVP 是否匿名设备号即可，还是必须登录？ | PM+Eng | R0 |
| OQ-3 | 免费用户每日最大局数？（防刷成本） | PM+Finance | R1 |
| OQ-4 | LLM 反馈上线节奏：R1 规则 vs R2 LLM？ | PM | R0 末 |
| OQ-5 | 首测市场：仅中文用户还是全球英文？ | PM | Discovery |
| OQ-6 | Passport 分享图品牌名定稿 | Design | R2 |
| OQ-7 | `identity-service` 何时接入正式账号 | Eng | Phase 2 |

---

## 附录 A：API 契约摘要（工程只读）

| 方法 | 路径 | 状态 |
|------|------|------|
| POST | `/v1/mobile/session/bootstrap` | ✅ 已实现 |
| POST | `/v1/mobile/sessions/{id}/turns` | ✅ 已实现 |
| GET | `/v1/mobile/sessions/{id}` | ✅ 已实现 |
| GET | `/healthz` | ✅ 已实现 |
| POST | `/v1/passport/stamps` | ❌ 待开发 |
| GET | `/v1/passport/stamps` | ❌ 待开发 |

---

## 附录 B：MVP 页面与路由（Mobile）

| 路由 | 屏幕 | 状态 |
|------|------|------|
| `/` | Home / Quest 入口 | ✅ 骨架 |
| `/role` | 岗位选择 | ✅ |
| `/mission` | 副本选择 | ✅ |
| `/interview` | 语音回合 | 🔶 需加录音 |
| `/feedback` | 反馈 | ✅ 需增强 |
| `/passport` | 护照章列表 | ❌ |
| `/onboarding` | 首次引导 | ❌ |

---

## 附录 C：工程交付物

- [prd-mvp-feature-list.md](./prd-mvp-feature-list.md) — **完整功能清单**（42 功能点 + API + P0 Gate）
- [prd-mvp-engineering-epics.md](./prd-mvp-engineering-epics.md) — R0–R3 Epic 清单、Fibonacci 估点、Sprint 计划
- [techspec-us004-voice-asr.md](./techspec-us004-voice-asr.md) — US-004 语音录制与 ASR 技术规格

## 附录 D：文档修订记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-17 | 初稿：基于 product-strategy + prd-development 工作流 |

---

*本 PRD 为工程与设计的执行真源之一；若与代码冲突，以已发布环境行为为准，并及时回写本文档。*
