import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View
} from "react-native";

import { ErrorBanner } from "@/components/ErrorBanner";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { StampEarnedModal } from "@/features/passport/StampEarnedModal";
import { FeedbackHelpfulPanel } from "@/features/feedback/FeedbackHelpfulPanel";
import { ScoreBreakdownPanel } from "@/features/feedback/ScoreBreakdownPanel";
import { StageNextPanel } from "@/features/feedback/StageNextPanel";
import { track } from "@/services/analytics";
import { fetchSessionDetail, type SessionDetail } from "@/services/api";
import { issueStampFromSession, type PassportStamp } from "@/storage/passportStamps";

export default function FeedbackScreen() {
  const { roleLabel, missionLabel, sessionId } = useLocalSearchParams<{
    roleLabel: string;
    missionLabel: string;
    sessionId: string;
  }>();
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [earnedStamp, setEarnedStamp] = useState<PassportStamp | null>(null);
  const [showStampModal, setShowStampModal] = useState(false);

  async function loadDetail() {
    if (!sessionId) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await fetchSessionDetail(sessionId);
      setDetail(result);

      const { stamp, isNew } = await issueStampFromSession({
        sessionId,
        missionId: result.missionId,
        missionLabel: missionLabel ?? result.missionId,
        roleId: result.roleId,
        roleLabel: roleLabel ?? result.roleId,
        detail: result
      });

      await track("feedback_view", {
        sessionId,
        readiness: result.scores.readiness
      });

      if (stamp && isNew) {
        setEarnedStamp(stamp);
        setShowStampModal(true);
        await track("passport_stamp_earned", {
          stampId: stamp.id,
          missionId: stamp.missionId
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDetail();
  }, [sessionId]);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Feedback</Text>
        <Text style={styles.title}>Your interview results</Text>
        <Text style={styles.subtitle}>
          {roleLabel} · {missionLabel}
        </Text>

        <LoadingOverlay
          visible={loading}
          message="Loading structured feedback…"
        />

        {!!error && (
          <ErrorBanner
            title="Could not load feedback"
            message={error}
            onRetry={() => void loadDetail()}
          />
        )}

        {!!detail && !loading && (
          <>
            <ScoreBreakdownPanel scores={detail.scores} />

            <StageNextPanel
              stage={detail.stage}
              currentQuestion={detail.currentQuestion}
              status={detail.status}
            />

            <FeedbackHelpfulPanel sessionId={sessionId} />

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Turn review</Text>
              {detail.turns.map((turn, index) => (
                <View key={`${turn.id}-${index}`} style={styles.turnBlock}>
                  <Text style={styles.turnLabel}>Question {index + 1}</Text>
                  <Text style={styles.turnQuestion}>{turn.question}</Text>
                  <Text style={styles.turnLabel}>Your answer</Text>
                  <Text style={styles.turnBody}>{turn.answer}</Text>
                  <View style={styles.feedbackBox}>
                    <Text style={styles.feedbackSummary}>{turn.feedback.summary}</Text>
                    <Text style={styles.feedbackTip}>{turn.feedback.improvementTip}</Text>
                  </View>
                </View>
              ))}
            </View>

            <View style={styles.ctaCard}>
              <Text style={styles.cardTitle}>What&apos;s next?</Text>
              <View style={styles.actions}>
                <Pressable
                  style={styles.button}
                  onPress={() =>
                    router.push({
                      pathname: "/quest-start",
                      params: {
                        roleId: detail.roleId,
                        roleLabel: roleLabel ?? detail.roleId,
                        missionId: detail.missionId,
                        missionLabel: missionLabel ?? detail.missionId
                      }
                    })
                  }
                >
                  <Text style={styles.buttonText}>Practice again</Text>
                </Pressable>
                <Pressable
                  style={styles.secondaryButton}
                  onPress={() => router.replace("/quest-map")}
                >
                  <Text style={styles.secondaryButtonText}>Quest Map</Text>
                </Pressable>
                <Pressable style={styles.secondaryButton} onPress={() => router.push("/passport")}>
                  <Text style={styles.secondaryButtonText}>Passport</Text>
                </Pressable>
              </View>
            </View>
          </>
        )}
      </ScrollView>

      <StampEarnedModal
        visible={showStampModal}
        stamp={earnedStamp}
        onViewPassport={() => {
          setShowStampModal(false);
          router.push("/passport");
        }}
        onDismiss={() => setShowStampModal(false)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { paddingHorizontal: 24, paddingTop: 48, paddingBottom: 48, gap: 16 },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700" },
  subtitle: { color: "#425466", fontSize: 16, marginBottom: 8 },
  loadingCard: { paddingVertical: 32, alignItems: "center", gap: 12 },
  loadingText: { color: "#425466", fontSize: 14 },
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  errorCard: { backgroundColor: "#fff1f0" },
  errorText: { color: "#9b2c2c", fontSize: 14, lineHeight: 20, marginBottom: 12 },
  cardTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 12 },
  turnBlock: {
    paddingBottom: 14,
    marginBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#f0dfc8"
  },
  turnLabel: {
    color: "#8a5a2b",
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 4
  },
  turnQuestion: {
    color: "#1d2a35",
    fontSize: 16,
    fontWeight: "600",
    lineHeight: 24,
    marginBottom: 10
  },
  turnBody: { color: "#425466", fontSize: 14, lineHeight: 22, marginBottom: 10 },
  feedbackBox: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#fffdf9",
    borderWidth: 1,
    borderColor: "#ead9c0"
  },
  feedbackSummary: { color: "#1d2a35", fontSize: 14, lineHeight: 21, marginBottom: 6 },
  feedbackTip: { color: "#6a7785", fontSize: 13, lineHeight: 20 },
  ctaCard: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
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
