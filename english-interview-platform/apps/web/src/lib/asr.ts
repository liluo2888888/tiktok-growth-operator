const WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions";
const TIMEOUT_MS = 30_000;

export class AsrError extends Error {
  constructor(
    readonly code: string,
    message: string
  ) {
    super(message);
    this.name = "AsrError";
  }
}

export type AsrResult = {
  transcript: string;
  durationMs: number;
};

function getOpenAiApiKey(): string | undefined {
  return import.meta.env.VITE_OPENAI_API_KEY?.trim() || undefined;
}

export function hasOpenAiApiKey(): boolean {
  return Boolean(getOpenAiApiKey());
}

export async function transcribeBlob(blob: Blob, durationMs: number): Promise<AsrResult> {
  const apiKey = getOpenAiApiKey();
  if (!apiKey) {
    throw new AsrError(
      "missing_api_key",
      "未配置 VITE_OPENAI_API_KEY，请改用手打或在本机 .env.local 中设置。"
    );
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const ext = blob.type.includes("webm") ? "webm" : "wav";
    const formData = new FormData();
    formData.append("file", blob, `recording.${ext}`);
    formData.append("model", "whisper-1");
    formData.append("language", "en");

    const response = await fetch(WHISPER_URL, {
      method: "POST",
      headers: { Authorization: `Bearer ${apiKey}` },
      body: formData,
      signal: controller.signal
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new AsrError("quota_exceeded", "语音 API 配额已用尽，请稍后再试。");
      }
      throw new AsrError("provider_error", `语音转写失败（${response.status}）`);
    }

    const payload = (await response.json()) as { text?: string };
    const transcript = (payload.text ?? "").trim();
    if (transcript.split(/\s+/).filter(Boolean).length < 3) {
      throw new AsrError("empty_audio", "未识别到足够英文内容，请重录或手打。");
    }

    return { transcript, durationMs };
  } catch (error) {
    if (error instanceof AsrError) throw error;
    if (error instanceof Error && error.name === "AbortError") {
      throw new AsrError("timeout", "转写超时，请检查网络后重试。");
    }
    throw new AsrError("provider_error", error instanceof Error ? error.message : "转写失败");
  } finally {
    window.clearTimeout(timeout);
  }
}
