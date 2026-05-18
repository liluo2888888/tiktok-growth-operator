import {
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View
} from "react-native";

import { LoadingOverlay } from "@/components/LoadingOverlay";
import type { useVoiceAnswer } from "@/features/interview/useVoiceAnswer";
import { MIN_RECORDING_SECONDS, MAX_RECORDING_SECONDS } from "@/features/interview/voiceConstants";

type VoiceAnswer = ReturnType<typeof useVoiceAnswer>;

type VoiceAnswerPanelProps = {
  voice: VoiceAnswer;
  submitting: boolean;
  onSubmit: () => void;
};

export function VoiceAnswerPanel({ voice, submitting, onSubmit }: VoiceAnswerPanelProps) {
  const isRecording = voice.phase === "recording";
  const canStartRecording = voice.phase === "ready" || voice.phase === "transcript_ready";
  const hasRecording = voice.phase === "recorded" || voice.phase === "transcribing";
  const showTranscript =
    voice.phase === "transcript_ready" ||
    voice.phase === "transcribe_failed" ||
    voice.phase === "transcribing";

  const remainingSeconds = Math.max(0, MAX_RECORDING_SECONDS - voice.recordingSeconds);

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Voice Answer</Text>
      <Text style={styles.cardBody}>
        Record at least {MIN_RECORDING_SECONDS} seconds (max {MAX_RECORDING_SECONDS}s), then review
        the transcript before submitting.
      </Text>
      {Platform.OS === "web" && (
        <Text style={styles.webHint}>
          Web demo: use Type Manually if the mic is unavailable, or paste your answer into the
          transcript box (at least 3 words) before Submit.
        </Text>
      )}

      <View style={styles.timerRow}>
        <View style={[styles.recordDot, isRecording && styles.recordDotActive]} />
        <Text style={styles.timerText}>
          {isRecording ? "Recording" : "Ready"} · {voice.recordingSeconds}s
          {isRecording ? ` · ${remainingSeconds}s left` : ""}
        </Text>
      </View>

            <View style={styles.actions}>
              {Platform.OS === "web" && (
                <Pressable style={styles.secondaryButton} onPress={voice.skipToManualEntry}>
                  <Text style={styles.secondaryButtonText}>Type answer (web)</Text>
                </Pressable>
              )}
              {canStartRecording && (
                <Pressable style={styles.button} onPress={() => void voice.beginRecording()}>
                  <Text style={styles.buttonText}>Start Recording</Text>
                </Pressable>
              )}
        {isRecording && (
          <Pressable style={styles.button} onPress={() => void voice.finishRecording()}>
            <Text style={styles.buttonText}>Stop</Text>
          </Pressable>
        )}
        {hasRecording && voice.phase === "recorded" && (
          <>
            <Pressable style={styles.secondaryButton} onPress={() => void voice.replay()}>
              <Text style={styles.secondaryButtonText}>
                {voice.isPlaying ? "Playing..." : "Replay"}
              </Text>
            </Pressable>
            <Pressable style={styles.button} onPress={() => void voice.runTranscription()}>
              <Text style={styles.buttonText}>Transcribe</Text>
            </Pressable>
            <Pressable style={styles.secondaryButton} onPress={() => void voice.resetVoice()}>
              <Text style={styles.secondaryButtonText}>Re-record</Text>
            </Pressable>
          </>
        )}
      </View>

      <LoadingOverlay
        visible={voice.phase === "transcribing"}
        message="Transcribing your answer…"
      />

      {!!voice.asrError && (
        <Text style={[styles.cardBody, styles.warningText]}>{voice.asrError}</Text>
      )}

      {showTranscript && (
        <>
          {voice.lowConfidence && (
            <Text style={styles.warningText}>
              Transcription may be inaccurate. Please review and edit before submitting.
            </Text>
          )}
          <TextInput
            multiline
            style={styles.input}
            value={voice.transcript}
            onChangeText={voice.setTranscript}
            placeholder="Your spoken answer will appear here..."
            placeholderTextColor="#9aa7b3"
            editable={voice.phase !== "transcribing"}
          />
          <View style={styles.actions}>
            <Pressable
              style={[
                styles.button,
                (!voice.canSubmitTranscript() || submitting) && styles.buttonDisabled
              ]}
              disabled={!voice.canSubmitTranscript() || submitting}
              onPress={onSubmit}
            >
              <Text style={styles.buttonText}>
                {submitting ? "Submitting..." : "Submit Answer"}
              </Text>
            </Pressable>
            <Pressable style={styles.secondaryButton} onPress={() => void voice.resetVoice()}>
              <Text style={styles.secondaryButtonText}>Re-record</Text>
            </Pressable>
          </View>
        </>
      )}

      {voice.phase === "transcribe_failed" && (
        <View style={styles.actions}>
          <Pressable style={styles.button} onPress={() => void voice.runTranscription()}>
            <Text style={styles.buttonText}>Retry Transcription</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={voice.skipToManualEntry}>
            <Text style={styles.secondaryButtonText}>Type Manually</Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginTop: 24,
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  cardTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 10 },
  cardBody: { color: "#425466", fontSize: 14, lineHeight: 20, marginBottom: 14 },
  timerRow: { flexDirection: "row", alignItems: "center", marginBottom: 14, gap: 8 },
  recordDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: "#c9b8a4"
  },
  recordDotActive: { backgroundColor: "#c0392b" },
  timerText: { color: "#1d2a35", fontSize: 15, fontWeight: "600" },
  input: {
    minHeight: 140,
    borderRadius: 16,
    backgroundColor: "#fffdf9",
    borderWidth: 1,
    borderColor: "#e5d4bd",
    paddingHorizontal: 14,
    paddingVertical: 14,
    color: "#1d2a35",
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 14,
    textAlignVertical: "top"
  },
  inlineStatus: { flexDirection: "row", alignItems: "center", gap: 10, marginTop: 4 },
  warningText: { color: "#8a5a2b", fontSize: 13, lineHeight: 18, marginBottom: 10 },
  webHint: {
    color: "#5c6f82",
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 12,
    padding: 10,
    borderRadius: 10,
    backgroundColor: "#eef3f8"
  },
  actions: { flexDirection: "row", gap: 10, flexWrap: "wrap" },
  button: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" }
});
