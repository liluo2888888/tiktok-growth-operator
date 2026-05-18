# P0 Gate 收尾清单（内测发布前）

| 字段 | 内容 |
|------|------|
| **版本** | v1.0 |
| **日期** | 2026-05-18 |
| **范围** | Interview Quest Pack MVP — **28 项 P0** |

完整功能矩阵见 [prd-mvp-feature-list.md](./prd-mvp-feature-list.md)。

---

## 一、自动化验收（必须先绿）

在仓库根目录执行：

```powershell
cd scripts
.\smoke-p0-gate.ps1
```

包含：

| 脚本 | 验证项 |
|------|--------|
| `smoke-r1-flow.ps1` | API-02 bootstrap、API-03 turn、API-04 session detail（scores + turns） |
| `smoke-passport-stamps.ps1` | API-05 章发放与列表 |
| `smoke-analytics-events.ps1` | API-07 埋点入库 |

移动端：

```powershell
cd apps\mobile
pnpm typecheck
pnpm test
```

---

## 二、P0 功能勾选（28 项）

### A 启动与引导
- [x] **A-01** 首次启动检测 → `/onboarding`
- [x] **A-02** 学习目标选择
- [x] **A-03** 岗位方向选择

### B 首页与导航
- [x] **B-01** 应用首页
- [x] **B-02** 主流程路由

### C Quest 副本
- [x] **C-01** Quest Pack 容器
- [x] **C-02** Quest Map
- [x] **C-03** Self-intro
- [x] **C-04** Behavioral
- [x] **C-05** 副本卡片状态

### D 面试 Session
- [x] **D-01** Session bootstrap
- [x] **D-02** 题目展示
- [x] **D-03** 文本答案提交
- [x] **D-04** Turn 持久化

### E 语音与 ASR
- [x] **E-01** 麦克风权限
- [x] **E-02** 录音计时
- [x] **E-04** ASR 转写（或 Web 手打）
- [x] **E-05** 转写预览/编辑
- [x] **E-06** 语音答案提交

### F 反馈与评分
- [x] **F-01** 反馈页加载
- [x] **F-02** 分数 breakdown
- [x] **F-03** 改进建议展示

### G Passport
- [x] **G-01** 章列表
- [x] **G-02** 章发放

### I 系统
- [x] **I-05** 隐私与语音说明（`/legal`）
- [x] **I-06** Session PostgreSQL（smoke-postgres-session.ps1 可选）

### API
- [x] **API-02** `POST /v1/mobile/session/bootstrap`
- [x] **API-03** `POST /v1/mobile/sessions/{id}/turns`
- [x] **API-04** `GET /v1/mobile/sessions/{id}`
- [x] **API-05** `POST/GET /v1/mobile/passport/stamps`

---

## 三、Web 全链路（已纳入自动化）

`scripts\smoke-p0-web.ps1`（由 `smoke-p0-gate.ps1` 调用）会：

1. 启动 file 后端 + gateway `:8090` + Vite `:5174`
2. 运行 `apps/web/scripts/walkthrough.mjs`（引导 → 任务 → **改用手打** → 反馈 → 护照）

本地手动演示：

```powershell
.\scripts\run-web-stack.cmd
```

浏览器：`http://127.0.0.1:5174` — 默认**语音作答**，可点「改用手打」；配置 `apps/web/.env.local` 中 `VITE_OPENAI_API_KEY` 可启用 Whisper 转写。

---

## 四、内测前建议核对（非 P0，但建议做）

| 项 | 说明 |
|----|------|
| I-03 埋点 | Web + Mobile 均已 `track()` → `POST /v1/mobile/analytics/events` |
| I-02 ErrorBanner | interview / feedback / passport 错误重试 |
| LoadingOverlay | 统一加载态（card + fullscreen） |
| 真机 | `setup-device-env.ps1` + `device-debug.ps1`（用户可选） |

---

## 五、明确不在 P0 Gate 内

- G-04 分享图（P1，原生截图）
- B-03 / H-01 / H-02 Streak（P1）
- A-04 onboarding 埋点（P1，已实现）
- API-06 readyz、I-07 错误 Envelope（P2）

---

## 六、签署

| 角色 | 姓名 | 日期 | 结果 |
|------|------|------|------|
| 工程 | | | ☐ Pass |
| 产品 | | | ☐ Pass |
