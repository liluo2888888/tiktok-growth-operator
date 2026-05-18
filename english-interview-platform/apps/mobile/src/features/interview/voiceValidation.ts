import { MIN_RECORDING_SECONDS } from "@/features/interview/voiceConstants";

export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export function canSubmitVoiceAnswer(
  transcript: string,
  recordingSeconds: number,
  minSeconds: number = MIN_RECORDING_SECONDS
): boolean {
  return countWords(transcript) >= 3 && recordingSeconds >= minSeconds;
}
