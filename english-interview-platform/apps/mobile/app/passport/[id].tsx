import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useRef, useState } from "react";
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
import { PassportStampCard } from "@/components/PassportStampCard";
import { ShareStampPoster } from "@/components/ShareStampPoster";
import { sharePassportStamp } from "@/features/passport/shareStamp";
import { readinessTier } from "@/features/passport/stampPresentation";
import { getPassportStamp, type PassportStamp } from "@/storage/passportStamps";
import { formatStampDate } from "@/utils/formatDate";

export default function PassportDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [stamp, setStamp] = useState<PassportStamp | null>(null);
  const [loading, setLoading] = useState(true);
  const [sharing, setSharing] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);
  const posterRef = useRef<View>(null);

  useEffect(() => {
    void (async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      setStamp(await getPassportStamp(id));
      setLoading(false);
    })();
  }, [id]);

  async function handleShare() {
    if (!stamp) {
      return;
    }

    setSharing(true);
    setShareError(null);

    try {
      await sharePassportStamp(stamp, posterRef);
    } catch (err) {
      setShareError(err instanceof Error ? err.message : "Could not open share sheet");
    } finally {
      setSharing(false);
    }
  }

  if (loading) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={[styles.container, styles.centered]}>
          <LoadingOverlay visible message="Loading stamp…" />
        </View>
      </SafeAreaView>
    );
  }

  if (!stamp) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.container}>
          <Text style={styles.title}>Stamp not found</Text>
          <Pressable style={styles.button} onPress={() => router.replace("/passport")}>
            <Text style={styles.buttonText}>Back to Passport</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Stamp detail</Text>
        <Text style={styles.title}>{stamp.missionLabel}</Text>
        <Text style={styles.body}>
          Earned {formatStampDate(stamp.earnedAt)} · {readinessTier(stamp.readiness)}
        </Text>

        <PassportStampCard stamp={stamp} />

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Score breakdown</Text>
          <ScoreRow label="Readiness" value={stamp.scores.readiness} highlight />
          <ScoreRow label="Clarity" value={stamp.scores.clarity} />
          <ScoreRow label="Structure" value={stamp.scores.structure} />
          <ScoreRow label="Confidence" value={stamp.scores.confidence} />
          <ScoreRow label="Relevance" value={stamp.scores.relevance} />
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Session</Text>
          <Text style={styles.meta}>Role: {stamp.roleLabel}</Text>
          <Text style={styles.meta}>Mission ID: {stamp.missionId}</Text>
          <Text style={styles.meta}>Session: {stamp.sessionId}</Text>
        </View>

        {!!shareError && (
          <ErrorBanner
            title="Share failed"
            message={shareError}
            onRetry={() => void handleShare()}
            retryLabel="Try again"
          />
        )}

        <LoadingOverlay
          visible={sharing}
          mode="fullscreen"
          message="Preparing share image…"
        />

        <View style={styles.actions}>
          <Pressable
            style={[styles.button, sharing && styles.buttonDisabled]}
            disabled={sharing}
            onPress={() => void handleShare()}
          >
            <Text style={styles.buttonText}>Share stamp</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => router.back()}>
            <Text style={styles.secondaryButtonText}>Back</Text>
          </Pressable>
        </View>

        <View style={styles.offscreen} pointerEvents="none">
          <ShareStampPoster ref={posterRef} stamp={stamp} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function ScoreRow({
  label,
  value,
  highlight
}: {
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <View style={styles.scoreRow}>
      <Text style={[styles.scoreLabel, highlight && styles.scoreLabelHighlight]}>{label}</Text>
      <Text style={[styles.scoreValue, highlight && styles.scoreValueHighlight]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { paddingHorizontal: 24, paddingTop: 48, paddingBottom: 40, gap: 16 },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 30, fontWeight: "700" },
  body: { color: "#425466", fontSize: 15, lineHeight: 22 },
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  cardTitle: { color: "#1d2a35", fontSize: 17, fontWeight: "600", marginBottom: 12 },
  meta: { color: "#6a7785", fontSize: 13, lineHeight: 20, marginBottom: 4 },
  scoreRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: "#f0dfc8"
  },
  scoreLabel: { color: "#425466", fontSize: 14 },
  scoreLabelHighlight: { color: "#1d2a35", fontWeight: "600" },
  scoreValue: { color: "#6a7785", fontSize: 14, fontWeight: "600" },
  scoreValueHighlight: { color: "#8a5a2b", fontSize: 18, fontWeight: "800" },
  actions: { gap: 10, marginTop: 4 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    alignSelf: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" },
  offscreen: {
    position: "absolute",
    left: -2000,
    top: 0,
    opacity: 0
  }
});
