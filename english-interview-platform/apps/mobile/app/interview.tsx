import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import {
  Linking,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View
} from "react-native";

import { ErrorBanner } from "@/components/ErrorBanner";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { DeviceDebugPanel } from "@/features/interview/DeviceDebugPanel";
import { VoiceAnswerPanel } from "@/features/interview/VoiceAnswerPanel";
import { useVoiceAnswer } from "@/features/interview/useVoiceAnswer";
import {
  createInterviewSession,
  fetchSessionDetail,
  submitInterviewTurn,
  type SessionBootstrap,
  type SessionDetail
} from "@/services/api";
import { track } from "@/services/analytics";
import { recordQuestCompletion } from "@/storage/streak";
import { markMissionCompleted } from "@/storage/userProfile";
import { withRetry } from "@/utils/retry";

export default function InterviewScreen() {
  const { roleId, roleLabel, missionId, missionLabel } = useLocalSearchParams<{
    roleId: string;
    roleLabel: string;
    missionId: string;
    missionLabel: string;
  }>();

  const [session, setSession] = useState<SessionBootstrap | null>(null);
  const [sessionDetail, setSessionDetail] = useState<SessionDetail | null>(null);
  const [bootstrapError, setBootstrapError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const voice = useVoiceAnswer();

  const currentQuestion =
    sessionDetail?.currentQuestion ?? "Your interview question will appear here.";

  async function handleStart() {
    setLoading(true);
    setBootstrapError(null);

    try {
      const bootstrap = await createInterviewSession({ roleId, missionId });
      setSession(bootstrap);
      await track("session_bootstrap", {
        sessionId: bootstrap.sessionId,
        missionId,
        roleId
      });
      const detail = await fetchSessionDetail(bootstrap.sessionId);
      setSessionDetail(detail);
      await voice.prepare();
    } catch (err) {
      setBootstrapError(err instanceof Error ? err.message : "Failed to start session");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void handleStart();
  }, []);

  async function handleSubmitTurn() {
    if (!session || !voice.canSubmitTranscript()) {
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const result = await withRetry(
        () =>
          submitInterviewTurn({
            sessionId: session.sessionId,
            answer: voice.transcript.trim()
          }),
        { maxAttempts: 3, baseDelayMs: 600 }
      );

      setSessionDetail(result);
      await markMissionCompleted(missionId);
      await recordQuestCompletion();
      const answer = voice.transcript.trim();
      await track("turn_submit", {
        sessionId: session.sessionId,
        durationSec: Math.max(1, Math.round(voice.recordingDurationMs / 1000)),
        wordCount: answer.split(/\s+/).filter(Boolean).length
      });
      await voice.cleanupAfterSubmit();

      router.replace({
        pathname: "/feedback",
        params: {
          roleLabel,
          missionLabel,
          sessionId: session.sessionId
        }
      });
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Voice Quest</Text>
        <Text style={styles.title}>Speak Your Answer</Text>
        <Text style={styles.body}>Role: {roleLabel}</Text>
        <Text style={styles.body}>Mission: {missionLabel}</Text>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Interview Question</Text>
          <Text style={styles.question}>{currentQuestion}</Text>
          {!!session && (
            <Text style={styles.meta}>Session: {session.sessionId}</Text>
          )}
          <View style={styles.actions}>
            <Pressable style={styles.secondaryButton} onPress={() => void handleStart()}>
              <Text style={styles.secondaryButtonText}>Restart Session</Text>
            </Pressable>
          </View>
        </View>

        <LoadingOverlay visible={loading} message="Starting session…" />

        {!!bootstrapError && (
          <ErrorBanner
            title="Could not start session"
            message={bootstrapError}
            onRetry={() => void handleStart()}
          />
        )}

        {!!submitError && (
          <ErrorBanner
            title="Submit failed"
            message={submitError}
            onRetry={() => void handleSubmitTurn()}
            retryLabel="Retry submit"
          />
        )}

        {voice.phase === "permission_denied" && (
          <View style={[styles.card, styles.errorCard]}>
            <Text style={styles.errorText}>
              Microphone access is required to practice speaking.
            </Text>
            <Pressable style={styles.button} onPress={() => Linking.openSettings()}>
              <Text style={styles.buttonText}>Open Settings</Text>
            </Pressable>
          </View>
        )}

        {!!session && !loading && voice.phase !== "permission_denied" && (
          <VoiceAnswerPanel
            voice={voice}
            submitting={submitting}
            onSubmit={() => void handleSubmitTurn()}
          />
        )}

        <LoadingOverlay
          visible={submitting}
          mode="fullscreen"
          message="Submitting your answer…"
        />

        {__DEV__ && (
          <DeviceDebugPanel onRetryBootstrap={() => void handleStart()} />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { paddingHorizontal: 24, paddingTop: 48, paddingBottom: 40 },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 10,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700", marginBottom: 12 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24 },
  card: {
    marginTop: 24,
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  errorCard: { backgroundColor: "#fff1f0" },
  cardTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 10 },
  cardBody: { color: "#425466", fontSize: 14, lineHeight: 20, marginBottom: 14 },
  question: {
    color: "#1d2a35",
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "600",
    marginBottom: 12
  },
  meta: { color: "#6b7c8f", fontSize: 12, marginBottom: 12 },
  errorText: { color: "#9b2c2c", fontSize: 14, lineHeight: 20, marginBottom: 12 },
  actions: { flexDirection: "row", gap: 10, flexWrap: "wrap" },
  button: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" }
});
