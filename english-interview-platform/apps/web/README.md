# Quest English — Web 前端

独立 **React + Vite** Web 应用，对接 `api-gateway`，与 `apps/mobile` 共用同一套面试主流程。界面为**中文**；面试题目与作答内容仍为英文。

设计遵循 `E:\前端\skills` 中的 **frontend-design**、**ui-ux-pro-max**、**teach-impeccable**：

- **编辑感面试教练**：Fraunces + IBM Plex Sans、暖色纸感、铜色强调
- **SVG 图标**（无 emoji 导航）、入场 stagger 动画、`prefers-reduced-motion`
- 设计真源：`.impeccable.md`、`design-system/MASTER.md`

## 一键启动（推荐）

在仓库根目录执行（会依次启动 session-service、api-gateway、Vite）：

```powershell
.\scripts\run-web-stack.cmd
```

或：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-web-stack.ps1
```

浏览器打开：**http://127.0.0.1:5174**

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| session-service | 8082 | `SESSION_REPOSITORY_BACKEND=file`，无需 Postgres |
| api-gateway | **8090** | 避开本机常被占用的 8080 |
| Vite | **5174** | 避开本机常被占用的 5173 |

可选环境变量：`WEB_PORT`、`GATEWAY_PORT`、`SESSION_PORT`。

仅启动前端（后端已运行时）：

```powershell
.\scripts\run-web-app.cmd
```

## 手动分步启动

**1. 后端**（两个终端，仓库根目录）：

```powershell
# 终端 A — 需 file 后端（无 Postgres 时）
$env:SESSION_REPOSITORY_BACKEND="file"
.\scripts\run-session-service.cmd

# 终端 B — 建议 8090
$env:API_GATEWAY_ADDR=":8090"
.\scripts\run-api-gateway.cmd
```

**2. 前端**：

```powershell
cd apps\web
$env:VITE_DEV_API="http://127.0.0.1:8090"
pnpm install
pnpm dev -- --port 5174 --host 127.0.0.1
```

## 页面流程

```text
/onboarding → /quest-map → /quest-start → /interview → /feedback → /passport
```

Web 使用**英文打字作答**（移动端保留语音）。本地状态在 `localStorage`（profile、streak、stamps）。

## 校验

```powershell
cd apps\web
pnpm typecheck
pnpm build
```

端到端 UI 走查（需先 `pnpm exec playwright install chromium`）：

```powershell
$env:WALKTHROUGH_BASE="http://127.0.0.1:5174"
node scripts/walkthrough.mjs
```

截图输出：`apps/web/walkthrough-screenshots/`。

## 与 Impeccable 的关系

[Impeccable](https://impeccable.style) 是**设计技能参考**（如何用 AI 做好前端视觉），不是本产品的代码库。本前端在 `english-interview-platform/apps/web`。
