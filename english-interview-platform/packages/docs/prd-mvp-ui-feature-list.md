# Quest English MVP — 按页面 UI 功能表

| 字段 | 内容 |
|------|------|
| **版本** | v1.0 |
| **日期** | 2026-05-17 |
| **CSV 导出** | [exports/prd-mvp-ui-by-screen.csv](./exports/prd-mvp-ui-by-screen.csv) |
| **功能矩阵 CSV** | [exports/prd-mvp-feature-matrix.csv](./exports/prd-mvp-feature-matrix.csv) |

> Excel 打开 CSV：请用「数据 → 从文本/CSV」并选 **UTF-8**，或直接双击（文件含 BOM，Windows Excel 可正确显示中文）。

---

## 页面流总览

```text
/onboarding (新) ──► / 或 /quest-map
       │
       ▼
/ (index) ──► /role ──► /mission ──► /interview ──► /feedback ──► /passport
                      (过渡)              │
                                          └──► /quest-start (可选)
```

**MVP 现状（2026-05-17）：** 主流程 `onboarding → quest-map → quest-start → interview → feedback → passport`；Web 可用手打答案跑通；`/role`、`/mission` 保留为遗留快捷路径。

---

## 1. 首页 `/` — `app/index.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| Hero | 标题 + 副文案 | B-01 | P0 | ✅ |
| CTA 卡 | Start Flow 按钮 | B-01, B-02 | P0 | ✅ |
| Streak | 连续天数 | H-01 | P1 | ✅ |
| Streak | 今日任务 / 推荐副本 | H-02, C-05 | P1 | ✅ |

---

## 2. 引导页 `/onboarding` — `app/onboarding.tsx`

| 步骤 | 元素 | 功能 ID | 优先级 | 状态 |
|------|------|---------|--------|------|
| 1 | 目标：Job Interview（默认选中） | A-02 | P0 | ✅ |
| 2 | 岗位：Product / General | A-03 | P0 | ✅ |
| 完成 | Continue → Quest Map；写本地配置 | A-01, A-04 | P0/P1 | ✅ / ❌ 埋点 |

---

## 3. 岗位选择 `/role` — `app/role.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 列表 | 岗位卡片 | A-03, C-01 | P0 | 🔶 |
| 底部 | Next → mission | B-02 | P0 | ✅ |

---

## 4. Quest Map `/quest-map` — `app/quest-map.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 顶栏 | Interview Quest Pack | C-01 | P0 | ✅ |
| 卡片 | Self-intro（标题/时长/状态） | C-03, C-05 | P0 | ✅ |
| 卡片 | Behavioral | C-04, C-05 | P0 | ✅ |
| 点击 | → Quest Start | C-06 | P1 | ✅ |

**过渡方案：** 继续用 `/mission` 直到 Map 页上线。

---

## 5. 副本选择 `/mission` — `app/mission.tsx`（过渡）

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 列表 | mission 卡片 | C-02~C-04 | P0 | 🔶 |
| 底部 | Start → interview | B-02 | P0 | ✅ |

---

## 6. 开局准备 `/quest-start` — `app/quest-start.tsx`（待建）

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 正文 | 本局目标、考官一句话 | C-06 | P1 | ❌ |
| CTA | 开始练习 | C-06 | P1 | ❌ |

---

## 7. 面试练习 `/interview` — `app/interview.tsx`（核心）

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 信息 | Role / Mission | D-02 | P0 | 🔶 |
| Session 卡 | bootstrap 状态、sessionId | D-01 | P0 | ✅ |
| Session 卡 | Restart / Go Feedback | D-05, F-01 | P1/P0 | ✅ |
| **题目区** | **currentQuestion 大标题** | D-02 | P0 | ❌ 待加强 |
| **录音区** | 权限 / Record / Stop / 计时 | E-01, E-02 | P0 | ❌ |
| 录音区 | 试听 | E-03 | P1 | ❌ |
| **转写区** | 可编辑 transcript | E-04, E-05 | P0 | ❌ |
| 提交 | Submit（语音主路径） | E-06, D-04 | P0 | 🔶 当前 TextInput |
| 状态 | Error + 重试 | E-07, I-02 | P1 | ✅ |

---

## 8. 反馈页 `/feedback` — `app/feedback.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 顶栏 | role / mission | F-01 | P0 | ✅ |
| 分数 | Readiness 大号 + 五维进度条 | F-03 | P0 | ✅ |
| 列表 | Turn review 卡片 | F-02 | P0 | ✅ |
| 阶段 | StageNextPanel | F-04 | P1 | ✅ |
| 评价 | Helpful / Not helpful | F-05 | P1 | ✅ |
| CTA | Practice again / Map / Passport | F-06 | P1 | ✅ |
| 弹层 | StampEarnedModal | G-01 | P0 | ✅ |

---

## 9. 护照 `/passport`

### 9.1 列表 `app/passport/index.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 列表 | 章卡片 | G-02 | P0 | ✅ |
| 空态 | 开始第一局 | G-02 | P0 | ✅ |

### 9.2 详情 `app/passport/[id].tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 详情 | mission / 日期 / readiness + 五维 | G-03 | P1 | ✅ |
| 分享 | Share stamp（图/文） | G-04, G-05 | P1 | ✅ |

---

## 10. 法律页 `/legal` — `app/legal.tsx`

| UI 区块 | 元素 | 功能 ID | 优先级 | 状态 |
|---------|------|---------|--------|------|
| 正文 | 隐私政策 + 语音第三方说明 | I-05 | P0 | ✅ |

---

## 11. 全局 UI 组件（跨页面）

| 组件 | 用途 | 功能 ID | 状态 |
|------|------|---------|------|
| `ErrorBanner` | API 失败 + 重试 | I-02 | ✅ |
| `LoadingOverlay` | bootstrap / ASR / submit | E-07, I-08 | ✅ |
| `analytics.track()` | 8 个漏斗事件 | I-03 | ✅ |

---

## 12. 页面 × 发布火车

| 页面 | R1 必须 | R2 必须 | R3 必须 |
|------|---------|---------|---------|
| index | ✅ Streak 卡片 + 推荐副本 | Streak 完整 | — |
| onboarding | ✅ 新建 | — | — |
| role / mission | ✅ 串联 | — | — |
| quest-map | ✅ 新建或升级 mission | — | — |
| interview | ✅ **语音 UI 全套** | — | — |
| feedback | ✅ 列表+分数 | 评价+Passport 弹层 | — |
| passport | — | ✅ 列表+分享 | — |
| legal | — | — | ✅ |

---

## 文档修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-17 | 初稿 + CSV 导出 |
