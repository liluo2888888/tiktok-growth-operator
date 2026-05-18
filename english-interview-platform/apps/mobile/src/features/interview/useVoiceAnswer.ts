import { useEffect, useRef, useState } from "react";
import type { Audio } from "expo-av";

import {
  deleteRecordingFile,
  discardRecording,
  playRecording,
  requestMicrophonePermission,
  startRecording,
  stopRecording
} from "@/audio/recorder";
import { AsrError, getAsrProvider, hasOpenAiApiKey } from "@/services/asr";
import { MAX_RECORDING_SECONDS, MIN_RECORDING_SECONDS } from "@/features/interview/voiceConstants";
import { canSubmitVoiceAnswer } from "@/features/interview/voiceValidation";

export type VoicePhase =
  | "idle"
  | "permission_denied"
  | "ready"
  | "recording"
  | "recorded"
  | "transcribing"
  | "transcript_ready"
  | "transcribe_failed";

export function useVoiceAnswer() {
  const [phase, setPhase] = useState<VoicePhase>("idle");
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [recordingUri, setRecordingUri] = useState<string | null>(null);
  const [recordingDurationMs, setRecordingDurationMs] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [lowConfidence, setLowConfidence] = useState(false);
  const [asrError, setAsrError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const playbackRef = useRef<Audio.Sound | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isRecordingRef = useRef(false);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      void discardRecording();
      void unloadPlayback();
    };
  }, []);

  async function unloadPlayback() {
    if (playbackRef.current) {
      await playbackRef.current.unloadAsync();
      playbackRef.current = null;
    }
    setIsPlaying(false);
  }

  async function prepare() {
    setAsrError(null);
    const granted = await requestMicrophonePermission();
    if (!granted) {
      setPhase("permission_denied");
      return;
    }
    setPhase("ready");
  }

  async function beginRecording() {
    setAsrError(null);
    await unloadPlayback();
    await startRecording();
    isRecordingRef.current = true;
    setRecordingUri(null);
    setRecordingDurationMs(0);
    setRecordingSeconds(0);
    setTranscript("");
    setLowConfidence(false);
    setPhase("recording");

    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      setRecordingSeconds((current) => {
        const next = current + 1;
        if (next >= MAX_RECORDING_SECONDS) {
          void finishRecording();
        }
        return next;
      });
    }, 1000);
  }

  async function finishRecording() {
    if (!isRecordingRef.current) {
      return;
    }

    isRecordingRef.current = false;

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    try {
      const result = await stopRecording();
      setRecordingUri(result.uri);
      setRecordingDurationMs(result.durationMs);
      const seconds = Math.max(1, Math.round(result.durationMs / 1000));
      setRecordingSeconds(seconds);

      if (seconds < MIN_RECORDING_SECONDS) {
        setAsrError(`Record at least ${MIN_RECORDING_SECONDS} seconds before submitting.`);
        setPhase("recorded");
        return;
      }

      await transcribeRecording(result.uri, result.durationMs);
    } catch (error) {
      setAsrError(error instanceof Error ? error.message : "Failed to stop recording");
      setPhase("ready");
    }
  }

  async function transcribeRecording(uri: string, durationMs: number) {
    setPhase("transcribing");
    setAsrError(null);

    if (!hasOpenAiApiKey()) {
      setTranscript("");
      setAsrError(
        "Auto-transcription is off. Type your answer below, or set EXPO_PUBLIC_OPENAI_API_KEY in apps/mobile/.env."
      );
      setPhase("transcript_ready");
      return;
    }

    try {
      const result = await getAsrProvider().transcribe(uri, durationMs);
      setTranscript(result.transcript);
      setLowConfidence(
        typeof result.confidence === "number" && result.confidence < 0.6
      );
      setPhase("transcript_ready");
    } catch (error) {
      if (error instanceof AsrError && error.code === "missing_api_key") {
        setTranscript("");
        setAsrError(error.message);
        setPhase("transcript_ready");
        return;
      }

      setAsrError(error instanceof Error ? error.message : "Transcription failed");
      setPhase("transcribe_failed");
    }
  }

  async function runTranscription() {
    if (!recordingUri) {
      return;
    }

    if (recordingSeconds < MIN_RECORDING_SECONDS) {
      setAsrError(`Record at least ${MIN_RECORDING_SECONDS} seconds before submitting.`);
      return;
    }

    await transcribeRecording(recordingUri, recordingDurationMs);
  }

  function skipToManualEntry() {
    setTranscript("");
    setRecordingSeconds(MIN_RECORDING_SECONDS);
    setAsrError("Type your answer below, then submit.");
    setPhase("transcript_ready");
  }

  async function replay() {
    if (!recordingUri || isPlaying) {
      return;
    }

    await unloadPlayback();
    setIsPlaying(true);
    playbackRef.current = await playRecording(recordingUri);
    playbackRef.current.setOnPlaybackStatusUpdate((status) => {
      if (!status.isLoaded) {
        return;
      }
      if (status.didJustFinish) {
        void unloadPlayback();
      }
    });
  }

  async function resetVoice() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    await unloadPlayback();
    isRecordingRef.current = false;
    await discardRecording();

    if (recordingUri) {
      await deleteRecordingFile(recordingUri);
    }

    setRecordingUri(null);
    setRecordingDurationMs(0);
    setRecordingSeconds(0);
    setTranscript("");
    setLowConfidence(false);
    setAsrError(null);
    setPhase("ready");
  }

  function canSubmitTranscript(): boolean {
    return canSubmitVoiceAnswer(transcript, recordingSeconds);
  }

  async function cleanupAfterSubmit() {
    await resetVoice();
  }

  return {
    phase,
    recordingSeconds,
    recordingDurationMs,
    transcript,
    setTranscript,
    lowConfidence,
    asrError,
    isPlaying,
    canSubmitTranscript,
    prepare,
    beginRecording,
    finishRecording,
    runTranscription,
    skipToManualEntry,
    replay,
    resetVoice,
    cleanupAfterSubmit
  };
}
