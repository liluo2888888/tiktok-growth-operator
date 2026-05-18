# English Interview Platform

面向英文求职面试训练的 App-first 平台，当前阶段优先把移动端 MVP 和 Go 后端主链路做实，再逐步扩到 AI feedback、课程体系、增长和商业化。

## README 位置

主 README 路径：

`D:\我的文档\Documents\Playground 4\english-interview-platform\README.md`

你换窗口之后，先看这几个文件就能无缝续上：

- `D:\我的文档\Documents\Playground 4\english-interview-platform\README.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\SKELETON_STATUS.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\packages\docs\product-strategy-global-english-app.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\packages\docs\prd-mvp-quest-english.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\packages\docs\prd-mvp-feature-list.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\packages\docs\prd-mvp-engineering-epics.md`
- `D:\我的文档\Documents\Playground 4\english-interview-platform\packages\docs\techspec-us004-voice-asr.md`
- `D:\我的文档\Documents\Playground 4\plans\active\2026-05-16-english-interview-go-rn-skeleton.md`

## 项目目标

先做一个“卖结果”的英文面试训练 App，不是泛英语学习工具。

第一阶段聚焦：

- 英文面试角色选择
- 面试任务选择
- AI 模拟问答
- 每轮结构化反馈
- Session 记录与复盘
- 面试 readiness 提升路径

不在第一阶段主打：

- 大而全背单词
- K12 / 四六级 / 高考全场景
- 复杂社区
- 重内容课程平台

## 当前完成进度

当前不是纯 skeleton 了，已经有一条能跑的纵向切片。

### 已完成

- 新项目目录已建立在 `english-interview-platform/`
- 技术栈已确定：
  - 移动端：React Native + Expo + TypeScript
- **Web 前端**：`apps/web`（React + Vite，中文 UI，默认端口 5174）
  - 一键本地启动：`scripts\run-web-stack.cmd`（file 后端 + gateway :8090 + Vite）
  - 详见 `apps/web/README.md`
  - 后端：Go 微服务
  - 主数据：PostgreSQL（本地 Web 可走 `SESSION_REPOSITORY_BACKEND=file`）
- 第一条 app-facing 主链路已经打通：
  - `mobile -> api-gateway -> session-service`
- 已实现接口：
  - `POST /v1/mobile/session/bootstrap`
  - `GET /v1/mobile/sessions/{id}`
  - `POST /v1/mobile/sessions/{id}/turns`
- Mobile 页面流已经有：
  - `index -> role -> mission -> interview -> feedback`
- Session 已经支持结构化 turn：
  - `turn.id`
  - `turn.createdAt`
  - `turn.speaker`
  - `turn.question`
  - `turn.answer`
  - `turn.feedback.summary`
  - `turn.feedback.improvementTip`
- Session 已经支持会话内状态：
  - `stage`
  - `currentQuestion`
- `session-service` 已经切为 `postgres` 默认后端
- `sqlite` 支持已经移除
- `file` 后端只保留为显式 fallback
- PowerShell 文件后端真烟测已经跑通：
  - `scripts/smoke-file-session.ps1`
- PostgreSQL 真烟测已经跑通（Docker 标准路径）：
  - `scripts/smoke-postgres-session.ps1`

### 已验证

- `session-service` 的 `go build ./...` 通过
- `api-gateway` 的 `go build ./...` 通过
- `apps/mobile` 的 `pnpm exec tsc --noEmit` 之前已通过
- 文件后端 smoke 已验证：
  - `bootstrap -> persist -> detail`
  - 返回 `stage/currentQuestion/turns`
  - 本地文件已落盘

### 正在推进

- 统一错误 envelope 与 `readyz`
- PRD 状态机与 feedback rubric 文档化
- history / AI feedback 模块

## 当前阻塞与真实状态

这里写清楚，后续窗口继续时不要重复踩坑。

### Go 运行时

- 全局 Go 环境是脏的
- 旧路径：`E:\goenv\go\bin\go.exe`
- 坏 `GOROOT` 曾指向不存在的 `C:\Program Files\Go`
- 当前 repo 级稳定路径：
  - `C:\toolchains\go1.24.3-tar\go`

### PostgreSQL 真烟测

标准路径：Docker + 隔离端口（`18080` / `18082` / `55432`）。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-postgres-session.ps1
```

历史环境问题（bundled Windows PostgreSQL 仍可作为备选，但不再推荐）：

- 系统 PostgreSQL 服务不可用
- 中文路径会污染 PostgreSQL Windows 二进制
- 复制整棵 `pgsql15-extract` 太慢；缺 `lib/` 会导致 `initdb` 失败

## Monorepo 目录

```text
apps/
  mobile/                # React Native + Expo app
services/
  api-gateway/           # App-facing gateway / BFF
  identity-service/      # Auth and profile
  session-service/       # Session orchestration and persistence
  interview-service/     # Missions and training records
  feedback-service/      # Scoring and structured feedback
  billing-service/       # Subscription and sprint packages
packages/
  contracts/             # Shared API contracts and event shapes
  docs/                  # ADRs and service design notes
infra/
  docker/                # Local infra compose files and init SQL
scripts/
  *.cmd / *.ps1          # Local run and smoke scripts
```

## 核心技术架构

### 移动端

- React Native
- Expo
- TypeScript
- 当前定位：
  - 单 App 承载用户 onboarding、练习、反馈、历史记录

建议后续模块：

- `app/(routes)` 页面路由
- `src/services` API client
- `src/features/interview` 面试流程状态
- `src/features/feedback` 反馈展示
- `src/features/history` 历史 session
- `src/features/auth` 登录与用户态

### 后端

- Go 微服务
- 当前已落地服务：
  - `api-gateway`
  - `session-service`
- 当前更偏“模块化微服务 skeleton”，不是全量拆分完成

建议边界：

- `api-gateway`
  - 面向 mobile 的聚合层
  - 协议转换
  - 错误封装
- `session-service`
  - interview session 生命周期
  - turn 持久化
  - stage / currentQuestion 状态推进
- `feedback-service`
  - LLM feedback
  - scoring rubric
  - redo suggestions
- `interview-service`
  - role / mission / question pack 管理
  - 模板化题库
- `identity-service`
  - 用户 / 登录 / profile
- `billing-service`
  - 订阅、套餐、支付状态

### 数据层

- 主库：PostgreSQL
- 缓存：Redis
- 异步：NATS

当前明确原则：

- 生产方向以 PostgreSQL 为主，不再向 `sqlite` 漂移
- `file` 只作为本机应急 fallback

### 实时与 AI 层

当前还没有接入真实 AI 面试引擎，只是结构先留好。

后续建议：

- Realtime interview orchestration
- LLM question generation
- Turn-level feedback generation
- Structured scoring
- Retry and fallback model routing

## 已落地接口能力

### `POST /v1/mobile/session/bootstrap`

作用：

- 创建一个 interview session
- 生成 `sessionId`
- 初始化 seed turns
- 返回初始状态

### `POST /v1/mobile/sessions/{id}/turns`

作用：

- 提交一轮回答
- 推进 session 内状态机
- 生成下一轮状态和反馈

### `GET /v1/mobile/sessions/{id}`

作用：

- 拉取完整 session 明细
- 返回结构化 turns
- 返回 stage 和 currentQuestion

## PRD 视角：已经明确的产品方向

产品本质不是“学英语”，而是“提高英文面试拿 offer 的概率”。

因此 PRD 的核心对象不是课程，而是：

- 目标岗位
- 目标面试轮次
- 目标结果
- 当前差距
- 提升路径

## PRD 待办任务

这部分是后续最重要的 backlog，换窗口后可以直接继续拆。

### P0：MVP 必须完成

- 明确核心用户画像
  - 海外求职用户
  - 外企求职用户
  - 需要英文面试表达训练的转岗用户
- 明确首发 use case
  - self intro
  - behavioral
  - case / problem solving
- 明确 session 完整状态机
  - 开场
  - 深挖
  - 追问
  - 收尾
  - 结束
- 明确 feedback 结构
  - 内容是否切题
  - 结构是否完整
  - 语言是否自然
  - 结果导向是否清晰
  - 下一轮改进建议
- 明确 history / replay 产品体验
- 明确 readiness score 的口径
- 明确 MVP 成功指标
  - session completion rate
  - repeat usage
  - feedback usefulness

### P1：体验层补齐

- 登录与用户体系
- 历史记录页
- session 列表页
- 弱网 / 重试 / 错误态
- loading / empty / fail UI
- 埋点设计
- 订阅入口与价值包装

### P1：AI 能力补齐

- 问题生成策略
- 反馈生成策略
- rubric 设计
- prompt 管理
- 模型路由与 fallback
- 成本控制
- 安全与内容审核

### P1：业务数据设计

- 用户
- interview session
- turn
- feedback
- readiness snapshot
- payment / subscription

### P2：增长与商业化

- 用户首周 onboarding
- 免费次数限制
- 订阅套餐设计
- 结果承诺型包装
- referral / 分享
- lesson / sprint 组合

## 技术待办任务

### 当前最高优先级

- 跑通 PostgreSQL 真烟测
- 固化 `smoke-postgres-session.ps1`
- 更新状态文档，把 postgres smoke 作为标准路径

### 后端

- 统一服务监听地址与依赖地址环境变量
- 统一错误响应 envelope
- 加 `healthz` / `readyz`
- 补 PostgreSQL migration 策略
- 补 repository test
- 补 service integration test
- 把 session 状态机从 demo 逻辑升级成正式 domain 规则

### 移动端

- API 错误处理
- feedback 页增强
- history 页
- profile 页
- session resume
- analytics 埋点

### 基础设施

- 本地 PostgreSQL 标准启动方式
- Docker 或等效本地方案
- `.env` 规范
- CI
- build / lint / smoke 流程

## 本地运行方式

优先使用 repo 脚本，不要信任全局环境。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev-env.ps1
```

```cmd
scripts\run-api-gateway.cmd
scripts\run-session-service.cmd
scripts\install-mobile.cmd
scripts\run-mobile.cmd
```

当前 smoke 脚本：

- `scripts/smoke-file-session.ps1`
- `scripts/smoke-postgres-session.ps1`

## 后续接着做的顺序

如果你换窗口回来，建议按这个顺序继续：

1. 先看本 README
2. 再看 `SKELETON_STATUS.md`
3. 再看 `plans/active/2026-05-16-english-interview-go-rn-skeleton.md`
4. 继续完成 PostgreSQL 真烟测
5. smoke 跑通后，开始补正式 PRD 文档和 MVP backlog 执行
6. 然后进入 AI feedback 和 history 模块

## 当前最关键的代码与文档入口

- [README.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/README.md)
- [SKELETON_STATUS.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/SKELETON_STATUS.md)
- [product-strategy-global-english-app.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/product-strategy-global-english-app.md) — 对标多邻国的全球英语 App 产品战略
- [prd-mvp-quest-english.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/prd-mvp-quest-english.md) — Interview Quest Pack MVP PRD（工程可执行）
- [prd-mvp-feature-list.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/prd-mvp-feature-list.md) — MVP 完整功能清单（42 项）
- [prd-mvp-ui-feature-list.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/prd-mvp-ui-feature-list.md) — 按页面 UI 功能表
- [exports/prd-mvp-feature-matrix.csv](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/exports/prd-mvp-feature-matrix.csv) — 功能矩阵（Excel）
- [prd-mvp-engineering-epics.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/prd-mvp-engineering-epics.md) — Epic 估点与 Sprint 计划
- [techspec-us004-voice-asr.md](/D:/我的文档/Documents/Playground%204/english-interview-platform/packages/docs/techspec-us004-voice-asr.md) — 语音/ASR 技术规格
- [2026-05-16-english-interview-go-rn-skeleton.md](/D:/我的文档/Documents/Playground%204/plans/active/2026-05-16-english-interview-go-rn-skeleton.md)
- [session-service main.go](/D:/我的文档/Documents/Playground%204/english-interview-platform/services/session-service/cmd/api/main.go)
- [postgres session_repository.go](/D:/我的文档/Documents/Playground%204/english-interview-platform/services/session-service/internal/infrastructure/postgres/session_repository.go)
- [api-gateway server.go](/D:/我的文档/Documents/Playground%204/english-interview-platform/services/api-gateway/internal/httpserver/server.go)
- [smoke-postgres-session.ps1](/D:/我的文档/Documents/Playground%204/english-interview-platform/scripts/smoke-postgres-session.ps1)
