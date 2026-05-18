# Quest English MVP — 工程 Epic 与估点清单

| 字段 | 内容 |
|------|------|
| **版本** | v1.0 |
| **日期** | 2026-05-17 |
| **关联 PRD** | [prd-mvp-quest-english.md](./prd-mvp-quest-english.md) |
| **功能清单** | [prd-mvp-feature-list.md](./prd-mvp-feature-list.md) |
| **技术附录** | [techspec-us004-voice-asr.md](./techspec-us004-voice-asr.md) |
| **估点尺度** | Fibonacci：**1** ≈ 0.5 天 · **2** ≈ 1 天 · **3** ≈ 1.5 天 · **5** ≈ 2–3 天 · **8** ≈ 1 周 · **13** ≈ 2 周（1 名全栈工程师，含联调） |

**团队假设：** 1 移动端 + 1 后端（可同人兼职）；设计/PM 并行 Discovery。

**总估点（MVP 全量）：** ~**89** 点 ≈ **10–12 周**（含 R0 Discovery；若 R0 Gate 失败则 R1+ 暂停）

---

## 发布火车总览

| 火车 | 周期 | 目标 | 估点合计 |
|------|------|------|---------|
| **R0** | W1–W4 | Discovery Gate + ASR Spike 通过 | 21 |
| **R1** | W5–W8 | 语音主路径 + 反馈增强可内测 | 34 |
| **R2** | W9–W10 | Passport + Streak + 埋点 | 21 |
| **R3** | W11–W12 | 内测修复 + 发布清单 | 13 |

---

## R0 — Discovery & 技术探针

### EPIC-R0-01：用户 Discovery（PM + 设计）

| ID | 标题（Jira/Linear） | 类型 | 点 | 依赖 |
|----|---------------------|------|-----|------|
| R0-101 | `[Discovery] 招募 10 名 P0 用户并签署访谈同意` | Task | 2 | — |
| R0-102 | `[Discovery] 执行 10 次 30min 访谈（脚本：卡住场景/付费意愿）` | Task | 5 | R0-101 |
| R0-103 | `[Discovery] 汇总洞察：愿每日练 3min 语音比例` | Task | 2 | R0-102 |
| R0-104 | `[Discovery] Wizard-of-Oz 反馈卡片可用率测试（n≥5）` | Task | 3 | R0-102 |
| R0-105 | `[Gate] Discovery 评审：是否进入 R1` | Milestone | — | R0-103 |

**Epic 验收：** ≥6/10 愿每日练；≥3/5 认为 WoZ 反馈「有帮助」。

---

### EPIC-R0-02：ASR 端到端 Spike（工程）

| ID | 标题 | 类型 | 点 | 依赖 |
|----|------|------|-----|------|
| R0-201 | `[Spike] 选型文档：expo-av 录音 + 云 ASR（见 techspec）` | Spike | 3 | — |
| R0-202 | `[Spike] 移动端录音 POC：≥10s m4a 本地落盘` | Story | 3 | R0-201 |
| R0-203 | `[Spike] ASR POC：英文转写 P95 <5s（短句 30s）` | Story | 5 | R0-202 |
| R0-204 | `[Spike] 串联现有 POST /turns（转写文本入 answer）` | Story | 3 | R0-203 |
| R0-205 | `[Gate] ASR Spike 评审：准确率/成本/延迟` | Milestone | — | R0-204 |

**Epic 验收：** 真机完成 `录音 → 转写 → submit turn → GET detail`；选型写入 techspec §8。

---

## R1 — 语音主路径与反馈（MVP 核心）

### EPIC-R1-01：移动端语音回合（US-004）

| ID | 标题 | 类型 | 点 | PRD | 依赖 |
|----|------|------|-----|-----|------|
| R1-101 | `[Mobile] 集成 expo-av 麦克风权限与录音状态机` | Story | 5 | US-004 | R0-205 |
| R1-102 | `[Mobile] VoiceRound UI：波形/计时/重录/提交` | Story | 5 | US-004 | R1-101 |
| R1-103 | `[Mobile] ASR 客户端模块（provider 抽象 + 错误重试）` | Story | 5 | US-004 | R0-203 |
| R1-104 | `[Mobile] 转写预览与手动编辑（低置信度提示）` | Story | 3 | US-004 | R1-103 |
| R1-105 | `[Mobile] 提交 turn 后导航 Feedback（替换 TextInput 主路径）` | Story | 3 | US-004, US-005 | R1-104 |
| R1-106 | `[Mobile] 弱网重试与麦克风拒绝引导` | Story | 3 | US-009 | R1-105 |
| R1-107 | `[QA] 语音路径冒烟：iOS 模拟器 + 1 台真机` | Task | 2 | — | R1-106 |

**Epic 验收：** US-004 全部 AC；`interview.tsx` 默认走语音而非打字。

> 实现细节见 [techspec-us004-voice-asr.md](./techspec-us004-voice-asr.md)

---

### EPIC-R1-02：Quest 流程与 Onboarding（US-001/002）

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R1-201 | `[Mobile] Onboarding：goal + roleId 持久化（AsyncStorage）` | Story | 3 | US-001 |
| R1-202 | `[Mobile] Quest Map：self_intro / behavioral 卡片与完成态` | Story | 5 | US-002 |
| R1-203 | `[Mobile] Quest Start 屏：副本文案 + 预计时长` | Story | 2 | US-002 |
| R1-204 | `[Mobile] 路由参数统一：questPackId=interview` | Task | 1 | §5.5 |

---

### EPIC-R1-03：反馈页增强（US-005）

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R1-301 | `[Mobile] Feedback：turn 列表 + summary/tip 排版` | Story | 3 | US-005 |
| R1-302 | `[Mobile] Scores 五维可视化（radar 或 bar）` | Story | 3 | US-005 |
| R1-303 | `[Mobile] 「有帮助/无帮助」+ 本地事件队列` | Story | 2 | US-005 |
| R1-304 | `[Mobile] 下一题/再练一局 CTA` | Story | 2 | US-005 |

---

### EPIC-R1-04：后端稳固（非功能）

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R1-401 | `[BE] 统一 API 错误 envelope（gateway + session）` | Story | 5 | NFR |
| R1-402 | `[BE] readyz + 依赖 PostgreSQL 健康检查` | Story | 2 | NFR |
| R1-403 | `[BE] session 集成测试（postgres docker smoke 进 CI）` | Story | 3 | — |
| R1-404 | `[BE] deviceId 匿名用户头（X-Device-Id）透传占位` | Story | 2 | OQ-2 |

---

## R2 — Passport、Streak、数据

### EPIC-R2-01：Passport 服务（US-006/007）

| ID | 标题 | 类型 | 点 | PRD | 依赖 |
|----|------|------|-----|-----|------|
| R2-101 | `[BE] passport_snapshots 表 + migration` | Story | 3 | US-006 | R1-404 |
| R2-102 | `[BE] POST/GET /v1/passport/stamps（gateway 代理）` | Story | 5 | US-006 | R2-101 |
| R2-103 | `[BE] 完成 session 后自动发章（session-service 钩子或客户端触发）` | Story | 3 | US-006 | R2-102 |
| R2-104 | `[Mobile] Passport 列表 + 章详情 UI` | Story | 5 | US-006 | R2-102 |
| R2-105 | `[Mobile] 分享图生成 + Share Sheet` | Story | 5 | US-007 | R2-104 |

---

### EPIC-R2-02：Streak（US-008）

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R2-201 | `[Mobile] 本地 streak 计算（UTC 日切 + 完成标记）` | Story | 3 | US-008 |
| R2-202 | `[Mobile] Home 展示 streak + 今日任务完成态` | Story | 2 | US-008 |

---

### EPIC-R2-03：埋点（§6.5）

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R2-301 | `[Mobile] analytics 封装（console / 后续接 PostHog）` | Story | 3 | §6.5 |
| R2-302 | `[Mobile] 漏斗 8 事件接入` | Story | 3 | §6.5 |
| R2-303 | `[PM] 内测看板指标定义（Sheet 或 Notion）` | Task | 1 | §6 |

---

## R3 — 内测与发布

### EPIC-R3-01：内测就绪

| ID | 标题 | 类型 | 点 | PRD |
|----|------|------|-----|-----|
| R3-101 | `[Legal] 隐私政策 + 语音数据说明（简版）` | Task | 2 | NFR |
| R3-102 | `[Mobile] TestFlight / 内测分发配置` | Task | 3 | — |
| R3-103 | `[QA] 全链路回归脚本（bootstrap→voice→feedback→passport）` | Task | 3 | — |
| R3-104 | `[Fix] 内测 P0 bug 缓冲` | Buffer | 5 | — |

---

## 依赖关系图（简图）

```text
R0 Discovery Gate ──► R1 Mobile Voice (US-004)
        │                      │
        └── ASR Spike ──────────┘
                               ▼
                    R1 Feedback + Quest Flow
                               ▼
                    R2 Passport / Streak / Analytics
                               ▼
                    R3 Beta + Legal
```

---

## Sprint 建议（2 周 Sprint × 6）

| Sprint | 目标 | 拉入 Epic/Story |
|--------|------|----------------|
| S1 | R0 完成 | R0-101~105, R0-201~205 |
| S2 | 语音 POC 产品化（上半） | R1-101~104 |
| S3 | 语音产品化（下半）+ Quest | R1-105~107, R1-201~204 |
| S4 | 反馈 + 后端 | R1-301~304, R1-401~404 |
| S5 | Passport | R2-101~105, R2-201~202 |
| S6 | 数据 + 内测 | R2-301~303, R3-101~104 |

---

## 风险缓冲与砍 scope 顺序

若延期，按以下顺序砍（先砍后不影响核心假设验证）：

1. R2-105 分享图美化 → 系统纯文本分享  
2. R1-302 雷达图 → 数字列表  
3. R2-202 Home streak 动效  
4. R1-401 错误 envelope → 保持现状  
5. **不可砍：** R1-101~105（语音主路径）、R0 Gate

---

## Linear 项目配置建议

| 字段 | 建议值 |
|------|--------|
| Team | Quest English |
| Project | MVP Interview Quest Pack |
| Labels | `mobile`, `backend`, `discovery`, `spike`, `gate` |
| Cycle | 2 weeks |
| Priority | P0 = R1 voice；P1 = Passport；P2 = polish |

**Issue 标题规范：** `[域] 动词 + 对象` — 与上表 ID 一致，便于与 PRD US-xxx 互链。

---

## 文档修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-17 | 初稿 |
