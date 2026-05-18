import { useEffect, useRef, useState } from "react";

import { AsrError, hasOpenAiApiKey, transcribeBlob } from "@/lib/asr";
import {
  canSubmitVoiceAnswer,
  MAX_RECORDING_SECONDS,
  MIN_RECORDING_SECONDS
} from "@/lib/voiceValidation";

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
  const [recordingBlob, setRecordingBlob] = useState<Blob | null>(null);
  const [recordingDurationMs, setRecordingDurationMs] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [lowConfidence, setLowConfidence] = useState(false);
  const [asrError, setAsrError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startedAtRef = useRef(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const isRecordingRef = useRef(false);

  useEffect(() => {
    return () => {
      cleanupStream();
      stopTimer();
      revokeObjectUrl();
    };
  }, []);

  function revokeObjectUrl() {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlaying(false);
  }

  function cleanupStream() {
    mediaRecorderRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  function stopTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  async function prepare() {
    setAsrError(null);
    if (!navigator.mediaDevices?.getUserMedia) {
      setPhase("permission_denied");
      setAsrError("当前浏览器不支持麦克风录音。");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setPhase("ready");
    } catch {
      setPhase("permission_denied");
      setAsrError("需要麦克风权限才能录音。你也可以改用手打。");
    }
  }

  async function beginRecording() {
    if (!streamRef.current) {
      await prepare();
      if (!streamRef.current) return;
    }

    setAsrError(null);
    revokeObjectUrl();
    chunksRef.current = [];
    setRecordingBlob(null);
    setRecordingDurationMs(0);
    setRecordingSeconds(0);
    setTranscript("");
    setLowConfidence(false);

    const recorder = new MediaRecorder(streamRef.current, { mimeType: pickMimeType() });
    mediaRecorderRef.current = recorder;
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };

    startedAtRef.current = Date.now();
    isRecordingRef.current = true;
    recorder.start(250);
    setPhase("recording");

    stopTimer();
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
    if (!isRecordingRef.current || !mediaRecorderRef.current) return;

    isRecordingRef.current = false;
    stopTimer();

    const recorder = mediaRecorderRef.current;
    const blob = await new Promise<Blob>((resolve, reject) => {
      recorder.onstop = () => {
        const type = recorder.mimeType || "audio/webm";
        resolve(new Blob(chunksRef.current, { type }));
      };
      recorder.onerror = () => reject(new Error("录音失败"));
      recorder.stop();
    });

    const durationMs = Math.max(1, Date.now() - startedAtRef.current);
    const seconds = Math.max(1, Math.round(durationMs / 1000));
    setRecordingBlob(blob);
    setRecordingDurationMs(durationMs);
    setRecordingSeconds(seconds);

    if (seconds < MIN_RECORDING_SECONDS) {
      setAsrError(`请至少录满 ${MIN_RECORDING_SECONDS} 秒再提交。`);
      setPhase("recorded");
      return;
    }

    await transcribeRecording(blob, durationMs);
  }

  async function transcribeRecording(blob: Blob, durationMs: number) {
    setPhase("transcribing");
    setAsrError(null);

    if (!hasOpenAiApiKey()) {
      setTranscript("");
      setAsrError("未配置自动转写。请在下方编辑英文，或设置 VITE_OPENAI_API_KEY。");
      setPhase("transcript_ready");
      return;
    }

    try {
      const result = await transcribeBlob(blob, durationMs);
      setTranscript(result.transcript);
      setLowConfidence(false);
      setPhase("transcript_ready");
    } catch (error) {
      if (error instanceof AsrError && error.code === "missing_api_key") {
        setTranscript("");
        setAsrError(error.message);
        setPhase("transcript_ready");
        return;
      }
      setAsrError(error instanceof Error ? error.message : "转写失败");
      setPhase("transcribe_failed");
    }
  }

  async function runTranscription() {
    if (!recordingBlob) return;
    if (recordingSeconds < MIN_RECORDING_SECONDS) {
      setAsrError(`请至少录满 ${MIN_RECORDING_SECONDS} 秒。`);
      return;
    }
    await transcribeRecording(recordingBlob, recordingDurationMs);
  }

  function skipToManualEntry() {
    setTranscript("");
    setRecordingSeconds(MIN_RECORDING_SECONDS);
    setAsrError(null);
    setPhase("transcript_ready");
  }

  async function replay() {
    if (!recordingBlob || isPlaying) return;
    revokeObjectUrl();
    objectUrlRef.current = URL.createObjectURL(recordingBlob);
    const audio = new Audio(objectUrlRef.current);
    audioRef.current = audio;
    audio.onended = () => {
      setIsPlaying(false);
    };
    setIsPlaying(true);
    try {
      await audio.play();
    } catch {
      setIsPlaying(false);
      setAsrError("无法回放录音。");
    }
  }

  async function resetVoice() {
    stopTimer();
    isRecordingRef.current = false;
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    revokeObjectUrl();
    cleanupStream();
    setRecordingBlob(null);
    setRecordingDurationMs(0);
    setRecordingSeconds(0);
    setTranscript("");
    setLowConfidence(false);
    setAsrError(null);
    setPhase("idle");
    await prepare();
  }

  function canSubmitTranscript() {
    return canSubmitVoiceAnswer(transcript, recordingSeconds);
  }

  return {
    phase,
    recordingSeconds,
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
    resetVoice
  };
}

function pickMimeType(): string {
  if (typeof MediaRecorder === "undefined") return "";
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
  for (const type of candidates) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return "";
}
