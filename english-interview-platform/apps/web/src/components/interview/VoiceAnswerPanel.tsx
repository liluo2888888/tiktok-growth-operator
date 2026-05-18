import { Button } from "@/components/ui/Button";
import type { useVoiceAnswer } from "@/hooks/useVoiceAnswer";
import { ui } from "@/lib/copy";
import { MAX_RECORDING_SECONDS, MIN_RECORDING_SECONDS } from "@/lib/voiceValidation";

type VoiceAnswer = ReturnType<typeof useVoiceAnswer>;

type Props = {
  voice: VoiceAnswer;
  submitting: boolean;
  onSubmit: () => void;
  onUseManual: () => void;
};

export function VoiceAnswerPanel({ voice, submitting, onSubmit, onUseManual }: Props) {
  const { interview: copy } = ui;
  const isRecording = voice.phase === "recording";
  const canStart =
    voice.phase === "ready" ||
    voice.phase === "transcript_ready" ||
    voice.phase === "transcribe_failed";
  const hasRecording = voice.phase === "recorded" || voice.phase === "transcribing";
  const showTranscript =
    voice.phase === "transcript_ready" ||
    voice.phase === "transcribe_failed" ||
    voice.phase === "transcribing";
  const remaining = Math.max(0, MAX_RECORDING_SECONDS - voice.recordingSeconds);

  return (
    <div className="voice-panel" data-testid="voice-answer-panel">
      <p className="panel-title">{copy.voiceTitle}</p>
      <p className="card-body">{copy.voiceHint(MIN_RECORDING_SECONDS, MAX_RECORDING_SECONDS)}</p>

      {voice.phase === "permission_denied" && (
        <p className="voice-warning" role="alert">
          {voice.asrError ?? copy.micDenied}
        </p>
      )}

      <div className="voice-timer-row">
        <span className={`voice-record-dot${isRecording ? " active" : ""}`} aria-hidden />
        <span className="word-count">
          {isRecording ? copy.recording : copy.ready} · {voice.recordingSeconds}s
          {isRecording ? ` · ${copy.remaining(remaining)}` : ""}
        </span>
      </div>

      <div className="voice-actions">
        <Button type="button" variant="secondary" onClick={onUseManual}>
          {copy.useManual}
        </Button>
        {canStart && (
          <Button type="button" onClick={() => void voice.beginRecording()}>
            {copy.startRecording}
          </Button>
        )}
        {isRecording && (
          <Button type="button" onClick={() => void voice.finishRecording()}>
            {copy.stopRecording}
          </Button>
        )}
        {hasRecording && voice.phase === "recorded" && (
          <>
            <Button type="button" variant="secondary" onClick={() => void voice.replay()}>
              {voice.isPlaying ? copy.playing : copy.replay}
            </Button>
            <Button type="button" onClick={() => void voice.runTranscription()}>
              {copy.transcribe}
            </Button>
            <Button type="button" variant="secondary" onClick={() => void voice.resetVoice()}>
              {copy.reRecord}
            </Button>
          </>
        )}
      </div>

      {voice.phase === "transcribing" && (
        <div className="loading-block panel panel-inset" style={{ marginTop: "1rem" }}>
          <span className="spinner" />
          {copy.transcribing}
        </div>
      )}

      {voice.asrError && voice.phase !== "permission_denied" && (
        <p className="voice-warning">{voice.asrError}</p>
      )}

      {showTranscript && (
        <>
          {voice.lowConfidence && <p className="voice-warning">{copy.lowConfidence}</p>}
          <label htmlFor="voice-transcript" className="textarea-label">
            {copy.transcriptLabel}
          </label>
          <textarea
            id="voice-transcript"
            className="textarea"
            value={voice.transcript}
            onChange={(e) => voice.setTranscript(e.target.value)}
            placeholder={copy.transcriptPlaceholder}
            disabled={voice.phase === "transcribing"}
          />
          <p className="word-count">{ui.common.minWords(3)}</p>
          <Button
            type="button"
            style={{ marginTop: "1rem" }}
            disabled={!voice.canSubmitTranscript() || submitting}
            onClick={onSubmit}
          >
            {submitting ? copy.submitting : copy.submit}
          </Button>
        </>
      )}
    </div>
  );
}
