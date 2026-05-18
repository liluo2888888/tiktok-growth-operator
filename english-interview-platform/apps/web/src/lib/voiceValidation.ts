export const MIN_RECORDING_SECONDS = 10;
export const MAX_RECORDING_SECONDS = 120;

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
