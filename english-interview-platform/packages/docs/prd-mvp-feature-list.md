# Quest English MVP — 功能清单（Feature List）

| 字段 | 内容 |
|------|------|
| **版本** | v1.1 |
| **日期** | 2026-05-17 |
| **最近更新** | 2026-05-18 — Streak + 分享图 + 埋点 + ErrorBanner |
| **产品范围** | Interview Quest Pack MVP |
| **关联 PRD** | [prd-mvp-quest-english.md](./prd-mvp-quest-english.md) |
| **状态图例** | ✅ 已实现 · 🔶 部分实现 · ❌ 待开发 · ⏸ 明确不做 |

**统计（MVP 范围内）：** 共 **42** 项功能点 · P0 **28** · P1 **12** · P2 **2**（仅列不做的对照）

### 导出文件（Excel / CSV）

| 文件 | 用途 |
|------|------|
| [exports/prd-mvp-feature-matrix.csv](./exports/prd-mvp-feature-matrix.csv) | **功能矩阵**（42 行，含模块/优先级/状态/US/Epic/路由/P0验收） |
| [exports/prd-mvp-api-matrix.csv](./exports/prd-mvp-api-matrix.csv) | **API 清单**（7 项） |
| [exports/prd-mvp-ui-by-screen.csv](./exports/prd-mvp-ui-by-screen.csv) | **按页面 UI 功能表**（50+ 行 UI 元素级） |
| [prd-mvp-ui-feature-list.md](./prd-mvp-ui-feature-list.md) | 页面 UI 功能表（Markdown 可读版） |

> Windows Excel：直接双击 CSV（已含 UTF-8 BOM）；若乱码，用「数据 → 从文本/CSV」选 UTF-8。

---

## 一、功能总览（按模块）

| 模块 | 功能点数 | P0 | 已实现 | 本版目标 |
|------|---------|-----|--------|---------|
| A. 启动与引导 | 4 | 3 | 3 | R1 |
| B. 首页与导航 | 3 | 2 | 2 | R1–R2 |
| C. Quest 副本与内容 | 6 | 5 | 6 | R1 |
| D. 面试 Session | 5 | 4 | 5 | R1 |
| E. 语音与 ASR | 7 | 6 | 6 | R0–R1 |
| F. 反馈与评分 | 6 | 5 | 6 | R1 |
| G. Passport 进步 | 5 | 4 | 5 | R2 |
| H. 习惯与留存 | 3 | 1 | 2 | R2 |
| I. 系统与质量 | 3 | 0 | 3 | R1–R3 |
| **合计** | **42** | **28** | **39** | — |

---

## 二、详细功能清单

### 模块 A：启动与引导（Onboarding）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| A-01 | 首次启动检测 | P0 | R1 | ✅ | US-001 | `/` 检测 AsyncStorage，未完成则 `replace` 至 `/onboarding` |
| A-02 | 学习目标选择 | P0 | R1 | ✅ | US-001 | `/onboarding` 默认 `Job Interview`；写入本地 `goal` |
| A-03 | 岗位方向选择 | P0 | R1 | ✅ | US-001 | `/onboarding` 选 `product` / `general`；写入 `roleId` |
| A-04 | 引导完成埋点 | P1 | R2 | ✅ | US-001 | 触发 `onboarding_complete`，带 `goal`、`roleId` |

---

### 模块 B：首页与导航（Home & Nav）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| B-01 | 应用首页入口 | P0 | R1 | ✅ | — | `/` 展示 Quest Pack + Open Quest Map / Passport |
| B-02 | 流程路由导航 | P0 | R1 | ✅ | — | `onboarding → quest-map → quest-start → interview → feedback → passport` |
| B-03 | 首页 Streak 与今日任务 | P1 | R2 | ✅ | US-008 | 展示连续天数、今日是否已完成 1 局、推荐下一副本 |

---

### 模块 C：Quest 副本与内容（Quest Pack）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| C-01 | Interview Quest Pack 容器 | P0 | R1 | ✅ | US-002 | `/quest-map` 展示 Interview Quest Pack |
| C-02 | Quest Map 列表页 | P0 | R1 | ✅ | US-002 | `/quest-map` 展示 `self_intro`、`behavioral` |
| C-03 | Self-intro 副本 | P0 | R1 | ✅ | US-002 | `missionId=self_intro`；题目集 3 问（domain 已配置） |
| C-04 | Behavioral 副本 | P0 | R1 | ✅ | US-002 | `missionId=behavioral`；题目集 3 问 |
| C-05 | 副本卡片信息 | P0 | R1 | ✅ | US-002 | 标题、副标题、~3/5 min、Not started / In progress / Completed |
| C-06 | Quest Start 准备页 | P1 | R1 | ✅ | US-002 | `/quest-start` 本局目标 + 考官一句话 + Begin Practice |

**内容配置（MVP 固定，非 CMS）：**

| missionId | 显示名 | 首题示例 | 阶段流 |
|-----------|--------|---------|--------|
| `self_intro` | Self Introduction | Tell me about yourself. | opening → deep_dive → closing |
| `behavioral` | Behavioral Interview | Tell me about a cross-functional challenge. | opening → deep_dive → closing |

---

### 模块 D：面试 Session（核心练习）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| D-01 | 创建 Session（Bootstrap） | P0 | R1 | ✅ | US-003 | `POST /v1/mobile/session/bootstrap`；返回 `sessionId`、状态、种子 turns |
| D-02 | 展示当前面试题 | P0 | R1 | ✅ | US-003 | interview 页独立 Question 卡片展示 `currentQuestion` |
| D-03 | Session 阶段推进 | P0 | R1 | ✅ | US-003 | `stage` / `currentQuestion` 随 turn 更新（后端 domain） |
| D-04 | 提交回答（Turn） | P0 | R1 | ✅ | US-004 | `POST .../turns`；当前支持文本，语音见模块 E |
| D-05 | 重启 Session | P1 | R1 | ✅ | — | interview 页「Restart Session」；重新 bootstrap |

---

### 模块 E：语音与 ASR（差异化核心）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| E-01 | 麦克风权限申请 | P0 | R1 | ✅ | US-004 | `expo-av` + `app.json` 文案；拒绝引导设置 |
| E-02 | 录音控制（开始/停止） | P0 | R1 | ✅ | US-004 | 10–120s；计时与剩余秒数 |
| E-03 | 录音回放 | P1 | R1 | ✅ | US-004 | Replay + Re-record |
| E-04 | ASR 语音转文字 | P0 | R1 | 🔶 | US-004 | Whisper 客户端；Web 可手打绕过 |
| E-05 | 转写稿预览与编辑 | P0 | R1 | ✅ | US-004 | 可编辑 transcript；低置信度提示 |
| E-06 | 语音提交 Turn | P0 | R1 | ✅ | US-004 | 转写 → `POST .../turns` |
| E-07 | 弱网重试 | P1 | R1 | ✅ | US-009 | `withRetry` ASR 2 次、turn 3 次 |

**⏸ 明确不做：** Hearts 体力值、开口次数付费墙（MVP 开口不限次）。

---

### 模块 F：反馈与评分（Feedback）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| F-01 | 加载 Session 详情 | P0 | R1 | ✅ | US-005 | `GET /v1/mobile/sessions/{id}` |
| F-02 | Turn 级反馈展示 | P0 | R1 | ✅ | US-005 | Turn review 卡片：问题 / 答案 / summary / tip |
| F-03 | 五维分数展示 | P0 | R1 | ✅ | US-005 | Readiness 大号 + 五维进度条 |
| F-04 | 阶段与下一题提示 | P1 | R1 | ✅ | US-005 | `StageNextPanel`：stage + 下一题 / 完成态 |
| F-05 | 反馈有用性评价 | P1 | R1 | ✅ | US-005 | Helpful / Not helpful（本地存储）；埋点待接 |
| F-06 | 再练一局 / 返回 Map | P1 | R1 | ✅ | US-005 | Practice again / Quest Map / Passport |

**评分逻辑（MVP）：** 规则引擎（`session-service` domain）；Phase 2 接 LLM rubric。

---

### 模块 G：Passport 进步体系（游戏化 · 结果感）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| G-01 | 局后发放护照章 | P0 | R2 | ✅ | US-006 | Feedback 加载后发章 + 弹层（本地 MVP） |
| G-02 | Passport 列表页 | P0 | R2 | ✅ | US-006 | `/passport` 列表 + 空态 CTA |
| G-03 | 章详情页 | P1 | R2 | ✅ | US-006 | `/passport/[id]` scores + session |
| G-04 | 分享图生成 | P1 | R2 | ✅ | US-007 | 图片含 mission、readiness、品牌名（原生截图；Web 文字） |
| G-05 | 系统分享面板 | P1 | R2 | ✅ | US-007 | Share Sheet + `passport_share` 埋点 |

**⏸ 明确不做（MVP）：** XP 经验条、语法技能树、全球排行榜。

---

### 模块 H：习惯与留存（Streak & Retention）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| H-01 | 个人连续练习天数 | P1 | R2 | ✅ | US-008 | UTC 日切；当日完成 1 局 +1；断签归零 |
| H-02 | 每日主任务提示 | P1 | R2 | ✅ | US-008 | 首页：「今日 Quest 未完成」 |
| H-03 | 推送提醒 | P2 | — | ⏸ | — | **Out of MVP**；Phase 2 |

**⏸ 明确不做（MVP）：** 小队共 Streak、公会 Boss 战。

---

### 模块 I：系统与质量（Platform）

| 功能 ID | 功能名称 | 优先级 | 发布 | 状态 | US | 说明与验收要点 |
|---------|---------|--------|------|------|-----|----------------|
| I-01 | 服务健康检查 | P1 | R1 | ✅ | — | `GET /healthz`（gateway + session-service） |
| I-02 | API 错误态与重试 UI | P1 | R1 | ✅ | US-009 | interview/feedback/passport 使用统一 `ErrorBanner` |
| I-03 | 漏斗埋点（8 事件） | P1 | R2 | ✅ | §6.5 | 客户端 `track()` + `POST /v1/mobile/analytics/events` |
| I-08 | 统一 LoadingOverlay | P1 | R2 | ✅ | — | card / fullscreen；interview·feedback·passport 等 |
| I-04 | 匿名设备标识 | P1 | R1 | ✅ | — | 客户端生成 `X-Device-Id`；Passport API 已使用 |
| I-05 | 隐私政策与语音说明 | P0 | R3 | ✅ | NFR | `/legal` 隐私与语音第三方说明 |
| I-06 | Session 持久化（PostgreSQL） | P0 | R1 | ✅ | — | `interview_sessions`；smoke 已通过 |
| I-07 | 统一错误 Envelope | P2 | R1 | ❌ | — | gateway 结构化 `{ error, code }` |

---

## 三、后端 / API 功能清单

| API ID | 能力 | 方法 & 路径 | 优先级 | 状态 | 关联功能 |
|--------|------|------------|--------|------|---------|
| API-01 | 健康检查 | `GET /healthz` | P1 | ✅ | I-01 |
| API-02 | 创建 Session | `POST /v1/mobile/session/bootstrap` | P0 | ✅ | D-01 |
| API-03 | 提交 Turn | `POST /v1/mobile/sessions/{id}/turns` | P0 | ✅ | D-04, E-06 |
| API-04 | 查询 Session | `GET /v1/mobile/sessions/{id}` | P0 | ✅ | F-01 |
| API-05 | 发放/查询护照章 | `POST/GET /v1/mobile/passport/stamps` | P0 | ✅ | G-01, G-02 |
| API-06 | Ready 检查 | `GET /readyz` | P2 | ❌ | I-07 |
| API-07 | 埋点入库 | `POST /v1/mobile/analytics/events` | P1 | ✅ | I-03 |
| API-07 | 音频直传转写 | `POST .../turns/audio` | — | ⏸ | Phase 2 |

**内部服务（session-service）：**

| 能力 | 状态 | 说明 |
|------|------|------|
| PostgreSQL 仓储 | ✅ | 默认后端 |
| File 仓储 fallback | ✅ | 仅显式 `SESSION_REPOSITORY_BACKEND=file` |
| Schema 自动迁移 | ✅ | `EnsureSchema` on startup |
| LLM 反馈生成 | ⏸ | MVP 规则引擎 |

---

## 四、功能 × 用户故事 × Epic 对照矩阵

| 功能 ID | 功能名称 | User Story | Epic（工程） |
|---------|---------|------------|--------------|
| A-01~04 | 引导 | US-001 | R1-201 |
| B-03 | 首页 Streak | US-008 | R2-201, R2-202 |
| C-01~06 | Quest Map | US-002 | R1-202, R1-203 |
| D-01~05 | Session | US-003 | 已有 + R1-105 |
| E-01~07 | 语音 ASR | US-004 | R1-101~107 |
| F-01~06 | 反馈 | US-005 | R1-301~304 |
| G-01~05 | Passport | US-006, US-007 | R2-101~105 |
| H-01~02 | Streak | US-008 | R2-201~202 |
| I-02~07 | 系统 | US-009 | R1-401~404, R3-101 |

---

## 五、按发布火车汇总（交付清单）

### R0（W1–W4）— 无用户可见功能上线

| 交付 | 类型 |
|------|------|
| Discovery 报告 | 文档 |
| ASR Spike 通过 | 技术 |
| 功能清单基线确认 | 本文档 v1.0 |

### R1（W5–W8）— 核心可练

| 必须交付功能 ID |
|----------------|
| A-01, A-02, A-03 |
| B-01, B-02 |
| C-01~C-04, C-05（C-06 可砍） |
| D-01~D-04 |
| **E-01, E-02, E-04, E-05, E-06**（全部 P0 语音） |
| F-01~F-03 |
| I-01, I-02 |

### R2（W9–W10）— 留存与证明

| 必须交付功能 ID |
|----------------|
| G-01~G-05（G-04 可砍为纯文本分享） |
| H-01, H-02 |
| B-03 |
| F-05, F-06 |
| I-03, I-04 |
| A-04 |

### R3（W11–W12）— 内测

| 必须交付功能 ID |
|----------------|
| I-05 |
| 全链路回归通过 |
| P0 功能 **100%** 验收 |

---

## 六、P0 功能验收检查表（上线 Gate）

内测发布前，以下 **28** 项 P0 须全部 ✅。完整步骤见 **[p0-gate-checklist.md](./p0-gate-checklist.md)**。

**一键自动化：**

```powershell
cd scripts
.\smoke-p0-gate.ps1
```

**Web 全链路（手动）：** `scripts/run-web.cmd` → onboarding → quest-map → Type answer (web) → Submit → feedback → passport。

---

## 七、Out of Scope 功能对照（防止范围蔓延）

| 功能 | 状态 | 替代/原因 |
|------|------|-----------|
| 单词/语法课程 | ⏸ | 战略聚焦面试楔子 |
| Hearts 限次 | ⏸ | 开口不限次差异化 |
| 全球排行榜 | ⏸ | Phase 2 小队 |
| 真人外教预约 | ⏸ | 成本高 |
| 订阅支付 | ⏸ | Phase 3 |
| 多语种学习 | ⏸ | 仅英语 |
| 自由对话 AI 考官 | ⏸ | MVP 固定题集 |
| 推送提醒 | ⏸ | Phase 2 |
| 小队/公会 | ⏸ | Phase 2 |

---

## 八、文档修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-17 | 初稿：42 项功能点 + API 清单 + 验收 Gate |
