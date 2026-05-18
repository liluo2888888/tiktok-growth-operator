import { StyleSheet, Text, View } from "react-native";

import { ScoreBar } from "@/components/ScoreBar";
import type { SessionDetail } from "@/services/api";
import { readinessTier } from "@/features/passport/stampPresentation";

type ScoreBreakdownPanelProps = {
  scores: SessionDetail["scores"];
};

export function ScoreBreakdownPanel({ scores }: ScoreBreakdownPanelProps) {
  return (
    <View style={styles.card}>
      <View style={styles.hero}>
        <View>
          <Text style={styles.heroLabel}>Interview readiness</Text>
          <Text style={styles.heroTier}>{readinessTier(scores.readiness)}</Text>
        </View>
        <Text style={styles.heroValue}>{scores.readiness}</Text>
      </View>
      <ScoreBar label="Clarity" value={scores.clarity} />
      <ScoreBar label="Structure" value={scores.structure} />
      <ScoreBar label="Confidence" value={scores.confidence} />
      <ScoreBar label="Relevance" value={scores.relevance} />
      <ScoreBar label="Readiness" value={scores.readiness} highlight />
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  hero: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 18,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#f0dfc8"
  },
  heroLabel: {
    color: "#8a5a2b",
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 4,
    fontWeight: "700"
  },
  heroTier: { color: "#1d2a35", fontSize: 16, fontWeight: "600" },
  heroValue: { color: "#8a5a2b", fontSize: 44, fontWeight: "800" }
});
