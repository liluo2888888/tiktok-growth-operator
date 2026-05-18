import { createWhisperProvider, hasOpenAiApiKey } from "@/services/asr/whisperProvider";
import type { AsrProvider } from "@/services/asr/types";

export { AsrError, type AsrResult } from "@/services/asr/types";
export { hasOpenAiApiKey } from "@/services/asr/whisperProvider";

let cachedProvider: AsrProvider | null = null;

export function getAsrProvider(): AsrProvider {
  if (!cachedProvider) {
    cachedProvider = createWhisperProvider();
  }
  return cachedProvider;
}
