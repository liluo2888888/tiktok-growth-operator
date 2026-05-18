# 技术规格：US-004 语音录制与 ASR 提交

| 字段 | 内容 |
|------|------|
| **版本** | v1.0 |
| **日期** | 2026-05-17 |
| **PRD** | [prd-mvp-quest-english.md](./prd-mvp-quest-english.md) §7.3 US-004 |
| **Epic** | [prd-mvp-engineering-epics.md](./prd-mvp-engineering-epics.md) EPIC-R1-01 |
| **现状** | `apps/mobile/app/interview.tsx` 使用 `TextInput` 提交 `answer` 文本 |

---

## 1. 目标与非目标

### 1.1 目标

- 用户在 **Voice Round** 通过 **麦克风录音** 完成面试回答。
- 录音经 **ASR** 转为英文文本，写入现有 `POST /v1/mobile/sessions/{id}/turns` 的 `answer` 字段。
- 满足 PRD 约束：录音 **10s–120s**；失败可重试；弱网最多 **2 次** 自动重试。
- MVP **不修改** session-service 契约（仍为纯文本 `answer`）；ASR 在客户端或独立 BFF 完成。

### 1.2 非目标（MVP）

- 服务端存储原始音频文件（Phase 2 可选）。
- 实时流式 ASR / OpenAI Realtime 双向对话。
- 发音逐音素打分（ELSA 级；后续 feedback-service）。
- 多语言 ASR（MVP 仅 **英语** 题目与作答）。

---

## 2. 架构概览

```text
┌─────────────────────────────────────────────────────────┐
│  apps/mobile (Expo)                                      │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐ │
│  │ VoiceRound   │───►│ AudioRecorder│───►│ AsrProvider  │ │
│  │ Screen       │    │ (expo-av)   │    │ (interface)  │ │
│  └──────┬───────┘    └─────────────┘    └──────┬───────┘ │
│         │                                        │         │
│         │         transcript (string)            │         │
│         ▼                                        ▼         │
│  ┌──────────────────────────────────────────────────────┐│
│  │ api.ts → submitInterviewTurn({ sessionId, answer })   ││
│  └──────────────────────────┬───────────────────────────┘│
└─────────────────────────────┼────────────────────────────┘
                              │ HTTP
                              ▼
                    ┌─────────────────┐
                    │  api-gateway    │
                    │  :8080          │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ session-service │
                    │  (unchanged)    │
                    └─────────────────┘
```

**原则：** 最小侵入——后端继续只处理文本 turn；语音是移动端（或未来 gateway）的前置步骤。

---

## 3. 录音模块（Mobile）

### 3.1 依赖

```json
{
  "expo-av": "~15.0.0",
  "expo-file-system": "~18.0.0"
}
```

（版本随 Expo SDK 52 对齐，实施时以 `npx expo install` 为准。）

### 3.2 权限

| 平台 | 权限 | 拒绝时 UX |
|------|------|-----------|
| iOS | `NSMicrophoneUsageDescription`（app.json） | 全屏说明 + 跳转设置 |
| Android | `RECORD_AUDIO` | 同上 |

### 3.3 录音参数（MVP 默认）

| 参数 | 值 | 说明 |
|------|-----|------|
| 格式 | `.m4a` (AAC) | expo-av 默认，体积小 |
| 采样率 | 44100 Hz | 可降至 16000 若 ASR 要求 |
| 声道 | mono | 口语足够 |
| 最大时长 | 120 s | 到达后自动 stop |
| 最小时长 | 10 s | 不足则禁用 Submit |

### 3.4 状态机

```text
idle → requesting_permission → ready
  ready → recording → recorded
  recorded → transcribing → transcript_ready | transcribe_failed
  transcript_ready → submitting → success | submit_failed
  * → idle (on cancel / restart)
```

| 状态 | UI |
|------|-----|
| `recording` | 计时器、红色指示、Stop |
| `recorded` | 回放按钮、Re-record、Submit |
| `transcribing` | Loading「正在识别…」 |
| `transcript_ready` | 可编辑 TextInput + 置信度提示 |
| `submitting` | 禁用按钮 |

### 3.5 文件生命周期

- 录音文件写入 `FileSystem.cacheDirectory/quest-recording-{timestamp}.m4a`。
- 提交成功或用户 Re-record 后 **删除** 缓存文件（隐私）。
- 不在相册/export 目录落盘。

---

## 4. ASR 模块

### 4.1 Provider 接口

```typescript
// apps/mobile/src/services/asr/types.ts

export type AsrResult = {
  transcript: string;
  confidence?: number; // 0–1，可选
  language?: string;
  durationMs: number;
};

export type AsrErrorCode =
  | "network"
  | "timeout"
  | "empty_audio"
  | "provider_error"
  | "quota_exceeded";

export interface AsrProvider {
  transcribe(localUri: string): Promise<AsrResult>;
}
```

### 4.2 MVP 推荐方案（R0 Spike 二选一）

| 方案 | 优点 | 缺点 | MVP 建议 |
|------|------|------|---------|
| **A. OpenAI Whisper API** | 英文准确率高、接入快 | 需 API Key、音频上传成本 | **默认首选** |
| **B. 设备端 whisper.cpp / RN 绑定** | 无上传、离线 | 包体大、集成复杂 | 备选 |
| **C. 云厂商（Azure/Google）** | 企业 SLA | 配置重 | Phase 2 |

**Spike 验收（R0-203）：** 30s 英文口语样本，WER 主观可懂；P95 延迟 <5s（4G 良好网络）。

### 4.3 方案 A 实现要点（Whisper）

```typescript
// apps/mobile/src/services/asr/whisperProvider.ts
// POST https://api.openai.com/v1/audio/transcriptions
// model: whisper-1
// file: recording.m4a
// language: en
```

| 项 | 要求 |
|----|------|
| API Key | **禁止** 硬编码；开发用 `.env` + `expo-constants` extra；生产用 EAS Secrets |
| 超时 | 30s |
| 重试 | 网络错误指数退避，最多 2 次 |
| 空结果 | `transcript.trim().length < 3` → `empty_audio` |

### 4.4 置信度与编辑

- Whisper 无原生 confidence 时：`confidence` 省略，UI 不显示百分比。
- 若 provider 返回 confidence 且 `< 0.6`：黄色提示「识别可能不准，请检查文稿」。
- 用户 **可编辑** 转写文本后再 Submit（PRD 风险缓解）。

---

## 5. 与现有 API 集成

### 5.1 不变契约

```http
POST /v1/mobile/sessions/{sessionId}/turns
Content-Type: application/json

{
  "answer": "<ASR transcript, possibly user-edited>"
}
```

响应：完整 `SessionDetail`（与 [api.ts](../../apps/mobile/src/services/api.ts) 类型一致）。

### 5.2 客户端调用序列

```typescript
async function submitVoiceTurn(sessionId: string, localUri: string) {
  const { transcript } = await asrProvider.transcribe(localUri);
  const answer = transcript.trim();
  if (answer.split(/\s+/).length < 3) {
    throw new Error("Answer too short");
  }
  return submitInterviewTurn({ sessionId, answer });
}
```

### 5.3 可选扩展（Out of MVP，文档预留）

```http
POST /v1/mobile/sessions/{id}/turns/audio
Content-Type: multipart/form-data
```

由 api-gateway 转 ASR 再调 session-service——当需隐藏 API Key 或统一计费时启用。

---

## 6. UI/UX 规格（interview 屏改造）

### 6.1 布局（替换 TextInput 主路径）

1. **Question 区**：`currentQuestion`（bootstrap 后可 GET detail 刷新）。  
2. **Recorder 区**：Record / Stop / 时长。  
3. **Transcript 区**（转写后）：可编辑多行文本。  
4. **Actions**：Re-record · Submit · View Feedback（session 已存在时）。

### 6.2 与路由参数

保持现有 `roleId`, `missionId`, `roleLabel`, `missionLabel`；`handleStart()` 仍在 mount 时 bootstrap。

### 6.3 成功后导航

- Submit 成功 → `router.replace({ pathname: "/feedback", params: { sessionId, ... } })`  
- 避免用户返回重复提交同一 turn（除非产品允许多 turn：当前 domain 支持多次 `AddTurn`）。

### 6.4 无障碍

- Record 按钮：`accessibilityLabel="Start recording answer"`  
- 计时器：`accessibilityLiveRegion="polite"`

---

## 7. 错误处理

| 场景 | 用户文案（EN） | 行为 |
|------|----------------|------|
| 无麦克风权限 | Enable microphone to practice speaking. | 打开设置 |
| 录音太短 | Record at least 10 seconds. | 禁用 Submit |
| ASR 失败 | Could not transcribe. Check connection and try again. | 重试 / Re-record |
| turn API 4xx/5xx | Something went wrong. Retry. | 最多 2 次自动重试 |
| 会话不存在 | Session expired. Start a new quest. | 回 Quest Map |

**日志：** 开发环境 `console.error` 含 `AsrErrorCode`；生产接 Sentry（Phase 2）。

---

## 8. 安全与隐私

| 项 | MVP |
|----|-----|
| 音频上传 | 仅发往 ASR provider（若用 Whisper） |
| 存储 | 不落服务端；客户端缓存用后删除 |
| 隐私政策 | 需声明「语音发送至第三方 ASR」 |
| API Key | 客户端方案有泄露风险；内测可接受，上架前迁 BFF |

---

## 9. 测试计划

### 9.1 单元 / 组件

- `AudioRecorder` 状态机转换表（含非法转换拒绝）。
- `asrProvider` mock：成功 / 超时 / 空文本。

### 9.2 集成

- Mock ASR → 真实 `submitInterviewTurn` → 本地 gateway + session-service。  
- 复用 `scripts/smoke-file-session.ps1` 逻辑，answer 改为 spike 固定长文本（语音路径人工测）。

### 9.3 手工矩阵

| # | 场景 | 预期 |
|---|------|------|
| T1 | 正常 30s 录音 → 提交 | Feedback 页有 turn |
| T2 | 8s 录音 | Submit 禁用 |
| T3 | 飞行模式 ASR | 错误提示 + 重试 |
| T4 | 编辑转写后提交 | 持久化编辑后文本 |
| T5 | 拒绝麦克风 | 引导设置 |

---

## 10. 实施任务拆分（对应 Epic）

| 任务 ID | 文件/模块 | 说明 |
|---------|-----------|------|
| R1-101 | `src/audio/recorder.ts` | expo-av 封装 |
| R1-102 | `app/interview.tsx` | UI + 状态机 |
| R1-103 | `src/services/asr/*` | Provider |
| R1-104 | `interview.tsx` | 转写编辑 |
| R1-105 | `interview.tsx` + `api.ts` | 导航 Feedback |

### 10.1 建议目录结构

```text
apps/mobile/src/
  audio/
    recorder.ts
    types.ts
  services/
    asr/
      types.ts
      whisperProvider.ts
      index.ts          # export getAsrProvider()
    api.ts              # 已有
```

---

## 11. 环境与配置

```bash
# apps/mobile/.env.development（不提交 git）
EXPO_PUBLIC_OPENAI_API_KEY=sk-...

# app.json / app.config.ts
extra: {
  openaiApiKey: process.env.EXPO_PUBLIC_OPENAI_API_KEY,
}
```

`.gitignore` 必须包含 `.env*`。

---

## 12. 开放问题（工程）

| ID | 问题 | 建议决策时点 |
|----|------|-------------|
| TS-1 | 上架前是否必须 BFF 代理 ASR | R1 末 Sprint 评审 |
| TS-2 | 是否记录 `durationSec` 到 analytics | R2-302 一并做 |
| TS-3 | bootstrap 后是否立即 GET detail 展示首问 | R1-102（建议：是） |

---

## 13. 文档修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-17 | 初稿 |
