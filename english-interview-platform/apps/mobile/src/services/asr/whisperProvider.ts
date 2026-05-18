import { AsrError, type AsrProvider, type AsrResult } from "@/services/asr/types";
import { withRetry } from "@/utils/retry";

const WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions";
const TIMEOUT_MS = 30_000;

function getOpenAiApiKey(): string | undefined {
  return process.env.EXPO_PUBLIC_OPENAI_API_KEY?.trim() || undefined;
}

export function hasOpenAiApiKey(): boolean {
  return Boolean(getOpenAiApiKey());
}

export function createWhisperProvider(): AsrProvider {
  return {
    transcribe: (localUri, durationMs) => transcribeWithWhisper(localUri, durationMs)
  };
}

async function transcribeWithWhisper(localUri: string, durationMs: number): Promise<AsrResult> {
  const apiKey = getOpenAiApiKey();
  if (!apiKey) {
    throw new AsrError(
      "missing_api_key",
      "Set EXPO_PUBLIC_OPENAI_API_KEY in apps/mobile/.env for automatic transcription."
    );
  }

  return withRetry(
    async () => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

      try {
        const formData = new FormData();
        formData.append(
          "file",
          {
            uri: localUri,
            name: "recording.m4a",
            type: "audio/m4a"
          } as unknown as Blob
        );
        formData.append("model", "whisper-1");
        formData.append("language", "en");

        const response = await fetch(WHISPER_URL, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${apiKey}`
          },
          body: formData,
          signal: controller.signal
        });

        if (!response.ok) {
          if (response.status === 429) {
            throw new AsrError("quota_exceeded", "Speech API quota exceeded. Try again later.");
          }
          throw new AsrError("provider_error", `Speech API failed: ${response.status}`);
        }

        const payload = (await response.json()) as { text?: string };
        const transcript = (payload.text ?? "").trim();

        if (transcript.split(/\s+/).filter(Boolean).length < 3) {
          throw new AsrError("empty_audio", "Could not detect enough speech. Please record again.");
        }

        return {
          transcript,
          durationMs
        };
      } catch (error) {
        if (error instanceof AsrError) {
          throw error;
        }
        if (error instanceof Error && error.name === "AbortError") {
          throw new AsrError("timeout", "Speech recognition timed out. Check your connection.");
        }
        throw new AsrError(
          "network",
          error instanceof Error ? error.message : "Speech recognition failed."
        );
      } finally {
        clearTimeout(timeout);
      }
    },
    { maxAttempts: 2, baseDelayMs: 800 }
  );
}
